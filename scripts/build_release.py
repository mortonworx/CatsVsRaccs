import os
import platform
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
ARTIFACTS = ROOT / "release-artifacts"
PACKAGE_ROOT = ROOT / "release-package"
PYPROJECT = ROOT / "pyproject.toml"
APP_NAME = "CatsVsRaccs"
APP_ICON_PNG = ROOT / "assets" / "app_icon.png"
APP_ICON_ICO = ROOT / "assets" / "app_icon.ico"


def project_version():
    env_version = os.environ.get("APP_VERSION")
    if env_version:
        return env_version.removeprefix("v")

    with PYPROJECT.open("rb") as handle:
        data = tomllib.load(handle)
    return data["project"]["version"]


def run(cmd):
    subprocess.run(cmd, check=True, cwd=ROOT)


def current_target():
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":
        if machine in {"arm64", "aarch64"}:
            return "macos-arm64"
        return "macos-x64"

    if system == "Windows":
        return "windows-x64"

    raise RuntimeError(f"Unsupported build platform: {system} {machine}")


def archive(path_to_package, artifact_base):
    ARTIFACTS.mkdir(exist_ok=True)

    if platform.system() == "Darwin":
        package_dir = PACKAGE_ROOT / artifact_base
        shutil.rmtree(package_dir, ignore_errors=True)
        package_dir.mkdir(parents=True, exist_ok=True)

        bundled_app = package_dir / f"{APP_NAME}.app"
        shutil.copytree(path_to_package, bundled_app)

        launcher = package_dir / f"Open {APP_NAME}.command"
        launcher.write_text(
            "\n".join([
                "#!/bin/bash",
                'set -e',
                'SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"',
                f'APP_PATH="$SCRIPT_DIR/{APP_NAME}.app"',
                'xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || true',
                'open "$APP_PATH"',
                "",
            ]),
            encoding="utf-8",
        )
        launcher.chmod(0o755)

        archive_path = shutil.make_archive(
            str(ARTIFACTS / artifact_base),
            "zip",
            root_dir=PACKAGE_ROOT,
            base_dir=artifact_base,
        )
    else:
        archive_path = shutil.make_archive(
            str(ARTIFACTS / artifact_base),
            "zip",
            root_dir=path_to_package.parent,
            base_dir=path_to_package.name,
        )

    return Path(archive_path)


def find_generated_app(expected_name):
    direct_path = DIST / expected_name
    if direct_path.is_dir():
        return direct_path

    bundle_matches = sorted(
        path for path in DIST.rglob("*.app")
        if path.is_dir()
    )
    if not bundle_matches:
        raise FileNotFoundError(f"Expected built app bundle under {DIST}")

    # Nuitka can emit a top-level bundle like "main.app" while placing the
    # requested output filename on the inner executable. We want the outer
    # bundle users can double-click, not the nested Mach-O file.
    package_path = min(bundle_matches, key=lambda path: (len(path.parts), str(path)))

    renamed_path = DIST / expected_name
    if package_path != renamed_path:
        if renamed_path.exists():
            shutil.rmtree(renamed_path)
        package_path.rename(renamed_path)
        return renamed_path

    return package_path


def main():
    version = project_version()
    target = current_target()
    artifact_base = f"{APP_NAME}-{version}-{target}"

    shutil.rmtree(DIST, ignore_errors=True)
    shutil.rmtree(BUILD, ignore_errors=True)
    shutil.rmtree(ARTIFACTS, ignore_errors=True)
    shutil.rmtree(PACKAGE_ROOT, ignore_errors=True)

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "main.py",
        "--standalone",
        "--enable-plugin=tk-inter",
        "--include-data-dir=assets=assets",
        f"--output-dir={DIST}",
    ]

    if platform.system() == "Darwin":
        app_name = f"{artifact_base}.app"
        cmd.extend([
            "--macos-create-app-bundle",
            f"--macos-app-icon={APP_ICON_PNG}",
            f"--output-filename={app_name}",
        ])
        package_path = None
    elif platform.system() == "Windows":
        exe_name = f"{artifact_base}.exe"
        cmd.extend([
            "--onefile",
            "--windows-console-mode=disable",
            f"--windows-icon-from-ico={APP_ICON_ICO}",
            f"--output-filename={exe_name}",
        ])
        package_path = DIST / exe_name
    else:
        raise RuntimeError(f"Unsupported build platform: {platform.system()}")

    run(cmd)

    if platform.system() == "Darwin":
        package_path = find_generated_app(app_name)

    if not package_path.exists():
        raise FileNotFoundError(f"Expected built package at {package_path}")

    archive_path = archive(package_path, artifact_base)
    print(f"Built {package_path}")
    print(f"Packaged {archive_path}")


if __name__ == "__main__":
    main()
