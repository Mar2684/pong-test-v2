"""Génération et lecture de sons en stdlib (WAV + lecteur OS)."""

import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

from pong import config

_SAMPLE_RATE = 44100


class SoundEngine:
    """Génère des fichiers WAV et les joue via le lecteur audio de l'OS."""

    def __init__(self) -> None:
        self.enabled = True
        self.sounds_dir = 'assets/sounds'
        self._loaded = False

    def _write_wav(self, filename: str, segments: list[tuple[float, float]]) -> None:
        """Écrit un WAV mono 16-bit contenant la concaténation des segments (freq, durée)."""
        frames = bytearray()
        for freq, duration in segments:
            n_samples = int(_SAMPLE_RATE * duration)
            for i in range(n_samples):
                t = i / _SAMPLE_RATE
                # enveloppe douce en début/fin pour éviter les clics
                edge = _SAMPLE_RATE * 0.005
                fade = min(1.0, i / edge, (n_samples - i) / edge)
                sample = math.sin(2.0 * math.pi * freq * t) * fade
                frames += struct.pack('<h', int(sample * 32767))
        with wave.open(filename, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(_SAMPLE_RATE)
            wav.writeframes(bytes(frames))

    def _generate_tone(self, freq: float, duration: float, filename: str) -> None:
        """Crée un fichier WAV mono 44100Hz avec une sinusoïde de fréquence freq."""
        self._write_wav(filename, [(freq, duration)])

    def load_sounds(self) -> None:
        """Crée le dossier assets/sounds et génère les sons s'ils sont absents."""
        if self._loaded:
            return
        os.makedirs(self.sounds_dir, exist_ok=True)
        targets = {
            'paddle.wav': [(880.0, 0.05)],
            'wall.wav': [(440.0, 0.03)],
            'point.wav': [(220.0, 0.15), (110.0, 0.15)],
            'let.wav': [(330.0, 0.1)],
        }
        for name, segments in targets.items():
            path = os.path.join(self.sounds_dir, name)
            if not os.path.exists(path):
                self._write_wav(path, segments)
        self._loaded = True

    def play(self, name: str) -> None:
        """Joue le son en arrière-plan ; fallback silencieux si lecteur indisponible."""
        if not self.enabled:
            return
        path = os.path.join(self.sounds_dir, f'{name}.wav')
        if not os.path.exists(path):
            return
        try:
            if sys.platform.startswith('linux'):
                cmd = ['aplay', path]
            elif sys.platform == 'darwin':
                cmd = ['afplay', path]
            elif sys.platform == 'win32':
                cmd = ['cmd', '/c', 'start', '', path]
            else:
                return
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            # fallback silencieux : aucun son ne doit faire planter le jeu
            pass
