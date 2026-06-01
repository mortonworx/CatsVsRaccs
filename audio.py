import shutil
import subprocess
import threading
from pathlib import Path


try:
    import winsound
except ImportError:  # pragma: no cover - only available on Windows
    winsound = None


class AudioManager:
    def __init__(self):
        self._music_key = None
        self._music_path = None
        self._music_process = None
        self._music_stop = threading.Event()
        self._music_thread = None
        self._player_cmd = self._detect_player()

    def play_sound(self, path):
        sound_path = Path(path)
        if not sound_path.exists():
            return

        if winsound is not None:
            thread = threading.Thread(
                target=winsound.PlaySound,
                args=(str(sound_path), winsound.SND_FILENAME),
                daemon=True,
            )
            thread.start()
            return

        if self._player_cmd is None:
            return

        subprocess.Popen(  # noqa: S603
            [self._player_cmd, str(sound_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def play_music(self, key, path):
        music_path = Path(path)
        if self._music_key == key and self._music_path == music_path:
            return

        self.stop_music()

        if not music_path.exists():
            return

        self._music_key = key
        self._music_path = music_path
        self._music_stop.clear()

        if winsound is not None:
            winsound.PlaySound(
                str(music_path),
                winsound.SND_ASYNC | winsound.SND_FILENAME | winsound.SND_LOOP,
            )
            return

        if self._player_cmd is None:
            return

        self._music_thread = threading.Thread(target=self._music_loop, daemon=True)
        self._music_thread.start()

    def stop_music(self):
        self._music_stop.set()

        if winsound is not None:
            winsound.PlaySound(None, 0)
        elif self._music_process is not None and self._music_process.poll() is None:
            self._music_process.terminate()

        self._music_process = None
        self._music_thread = None
        self._music_key = None
        self._music_path = None

    def shutdown(self):
        self.stop_music()

    def _music_loop(self):
        while not self._music_stop.is_set() and self._music_path is not None:
            self._music_process = subprocess.Popen(  # noqa: S603
                [self._player_cmd, str(self._music_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._music_process.wait()
            if self._music_stop.is_set():
                break

    def _detect_player(self):
        for candidate in ("afplay", "paplay", "aplay"):
            player = shutil.which(candidate)
            if player is not None:
                return player
        return None
