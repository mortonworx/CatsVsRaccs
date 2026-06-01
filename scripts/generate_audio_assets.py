import math
import random
import wave
from array import array
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT / "assets" / "audio"
SFX_DIR = AUDIO_DIR / "sfx"
MUSIC_DIR = AUDIO_DIR / "music"
SAMPLE_RATE = 44100


def clamp(value, low=-1.0, high=1.0):
    return max(low, min(high, value))


def envelope(t, duration, attack=0.01, release=0.08):
    if t < 0 or t > duration:
        return 0.0
    attack = max(attack, 1e-6)
    release = max(release, 1e-6)
    if t < attack:
        return t / attack
    if t > duration - release:
        return max(0.0, (duration - t) / release)
    return 1.0


def sine(freq, t):
    return math.sin(2 * math.pi * freq * t)


def square(freq, t):
    return 1.0 if sine(freq, t) >= 0 else -1.0


def triangle(freq, t):
    return 2 * abs(2 * ((freq * t) % 1) - 1) - 1


def noise():
    return random.uniform(-1.0, 1.0)


def lowpass(samples, alpha=0.2):
    out = []
    prev = 0.0
    for sample in samples:
        prev = prev + alpha * (sample - prev)
        out.append(prev)
    return out


def write_wav(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = array("h")
    for sample in samples:
        pcm.append(int(clamp(sample) * 32767))
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm.tobytes())


def render(duration, sample_fn):
    total = int(SAMPLE_RATE * duration)
    return [sample_fn(i / SAMPLE_RATE) for i in range(total)]


def mix_layers(*layers):
    length = max(len(layer) for layer in layers)
    out = [0.0] * length
    for layer in layers:
        for i, sample in enumerate(layer):
            out[i] += sample
    peak = max(max(abs(s) for s in out), 1.0)
    return [s / peak * 0.9 for s in out]


def melodic_loop(chords, lead_notes, duration_per_bar, bass_gain=0.22, lead_gain=0.18, pad_gain=0.14):
    total_duration = duration_per_bar * len(chords)

    def pad_layer(t):
        bar = min(int(t / duration_per_bar), len(chords) - 1)
        local_t = t - bar * duration_per_bar
        chord = chords[bar]
        amp = envelope(local_t, duration_per_bar, attack=0.06, release=0.12)
        value = sum(sine(freq, t) for freq in chord) / len(chord)
        return value * amp * pad_gain

    def bass_layer(t):
        beat = int(t / 0.5)
        bar = min(int(t / duration_per_bar), len(chords) - 1)
        root = chords[bar][0] / 2
        local_t = t - beat * 0.5
        amp = envelope(local_t, 0.5, attack=0.01, release=0.15)
        return triangle(root, t) * amp * bass_gain

    def lead_layer(t):
        step = int(t / 0.25)
        note = lead_notes[step % len(lead_notes)]
        local_t = t - step * 0.25
        amp = envelope(local_t, 0.25, attack=0.004, release=0.08)
        wobble = sine(5, t) * 0.015
        return square(note + wobble, t) * amp * lead_gain

    def percussion_layer(t):
        value = 0.0
        beat_pos = t % 0.5
        if beat_pos < 0.04:
            value += noise() * (1 - beat_pos / 0.04) * 0.12
        hat_pos = t % 0.25
        if hat_pos < 0.012:
            value += noise() * (1 - hat_pos / 0.012) * 0.05
        return value

    layers = [
        render(total_duration, pad_layer),
        render(total_duration, bass_layer),
        render(total_duration, lead_layer),
        lowpass(render(total_duration, percussion_layer), alpha=0.35),
    ]
    return mix_layers(*layers)


def sfx_select():
    duration = 0.12

    def fn(t):
        freq = 740 + 340 * (t / duration)
        return sine(freq, t) * envelope(t, duration, attack=0.002, release=0.05) * 0.5

    return render(duration, fn)


def sfx_spawn():
    duration = 0.24

    def fn(t):
        pop = sine(220 + 80 * math.exp(-8 * t), t)
        sparkle = square(880 - 250 * t, t)
        return (pop * 0.45 + sparkle * 0.12) * envelope(t, duration, attack=0.005, release=0.12)

    return render(duration, fn)


def sfx_attack():
    duration = 0.16

    def fn(t):
        freq = 900 - 650 * (t / duration)
        swipe = triangle(freq, t) * 0.3
        grit = noise() * 0.2
        return (swipe + grit) * envelope(t, duration, attack=0.001, release=0.08)

    return lowpass(render(duration, fn), alpha=0.22)


def sfx_hit():
    duration = 0.18

    def fn(t):
        thump = sine(160 - 55 * t, t) * 0.45
        crack = noise() * 0.22
        return (thump + crack) * envelope(t, duration, attack=0.001, release=0.1)

    return lowpass(render(duration, fn), alpha=0.28)


def sfx_breakthrough():
    duration = 0.5

    def fn(t):
        pitch = 360 + 420 * (t / duration)
        chime = sine(pitch, t) * 0.32
        tail = sine(pitch * 1.5, t) * 0.18
        return (chime + tail) * envelope(t, duration, attack=0.005, release=0.18)

    return render(duration, fn)


def sfx_not_enough():
    duration = 0.22

    def fn(t):
        freq = 420 - 120 * (t / duration)
        return square(freq, t) * envelope(t, duration, attack=0.002, release=0.1) * 0.28

    return render(duration, fn)


def sfx_win():
    notes = [523.25, 659.25, 783.99, 1046.5]
    step = 0.14
    total = step * len(notes) + 0.1

    def fn(t):
        idx = min(int(t / step), len(notes) - 1)
        local_t = t - idx * step
        return (
            sine(notes[idx], t) * 0.34
            + triangle(notes[idx] / 2, t) * 0.12
        ) * envelope(local_t, step, attack=0.004, release=0.08)

    return render(total, fn)


def sfx_lose():
    notes = [329.63, 293.66, 246.94]
    step = 0.2
    total = step * len(notes) + 0.14

    def fn(t):
        idx = min(int(t / step), len(notes) - 1)
        local_t = t - idx * step
        return (
            square(notes[idx], t) * 0.18
            + sine(notes[idx] / 2, t) * 0.22
        ) * envelope(local_t, step, attack=0.003, release=0.12)

    return render(total, fn)


def generate():
    title = melodic_loop(
        chords=[
            (261.63, 329.63, 392.00),
            (293.66, 369.99, 440.00),
            (220.00, 277.18, 329.63),
            (246.94, 311.13, 392.00),
        ],
        lead_notes=[523.25, 659.25, 587.33, 659.25, 493.88, 587.33, 440.00, 493.88],
        duration_per_bar=2.0,
    )
    battle = melodic_loop(
        chords=[
            (220.00, 277.18, 329.63),
            (246.94, 311.13, 369.99),
            (196.00, 246.94, 293.66),
            (220.00, 277.18, 329.63),
        ],
        lead_notes=[440.00, 493.88, 523.25, 493.88, 587.33, 523.25, 493.88, 440.00],
        duration_per_bar=1.5,
        bass_gain=0.26,
        lead_gain=0.16,
        pad_gain=0.12,
    )
    expert = melodic_loop(
        chords=[
            (196.00, 246.94, 311.13),
            (233.08, 293.66, 349.23),
            (185.00, 233.08, 293.66),
            (207.65, 261.63, 329.63),
        ],
        lead_notes=[392.00, 466.16, 523.25, 466.16, 587.33, 523.25, 466.16, 415.30],
        duration_per_bar=1.25,
        bass_gain=0.28,
        lead_gain=0.18,
        pad_gain=0.10,
    )

    write_wav(MUSIC_DIR / "title_theme.wav", title)
    write_wav(MUSIC_DIR / "battle_theme.wav", battle)
    write_wav(MUSIC_DIR / "expert_theme.wav", expert)
    write_wav(SFX_DIR / "ui_select.wav", sfx_select())
    write_wav(SFX_DIR / "spawn_unit.wav", sfx_spawn())
    write_wav(SFX_DIR / "attack_swipe.wav", sfx_attack())
    write_wav(SFX_DIR / "hit_impact.wav", sfx_hit())
    write_wav(SFX_DIR / "turf_breakthrough.wav", sfx_breakthrough())
    write_wav(SFX_DIR / "not_enough_energy.wav", sfx_not_enough())
    write_wav(SFX_DIR / "win_jingle.wav", sfx_win())
    write_wav(SFX_DIR / "lose_sting.wav", sfx_lose())


if __name__ == "__main__":
    random.seed(7)
    generate()
