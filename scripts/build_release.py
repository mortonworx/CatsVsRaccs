import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
ARTIFACTS = ROOT / "release-artifacts"
VERSION = os.environ.get("APP_VERSION", "0.0.1rc1")
APP_NAME = "CatsVsRaccs"
APP_ICON_PNG = ROOT / "assets" / "app_icon.png"
APP_ICON_ICO = ROOT / "assets" / "app_icon.ico"


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
    archive_path = shutil.make_archive(
        str(ARTIFACTS / artifact_base),
        "zip",
        root_dir=path_to_package.parent,
        base_dir=path_to_package.name,
    )
    return Path(archive_path)


def main():
    target = current_target()
    artifact_base = f"{APP_NAME}-{VERSION}-{target}"

    shutil.rmtree(DIST, ignore_errors=True)
    shutil.rmtree(BUILD, ignore_errors=True)
    shutil.rmtree(ARTIFACTS, ignore_errors=True)

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
        package_path = DIST / app_name
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

    if not package_path.exists():
        raise FileNotFoundError(f"Expected built package at {package_path}")

    archive_path = archive(package_path, artifact_base)
    print(f"Built {package_path}")
    print(f"Packaged {archive_path}")


if __name__ == "__main__":
    main()
