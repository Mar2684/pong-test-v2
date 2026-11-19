"""Capture des entrées clavier tkinter."""

import tkinter as tk


class InputHandler:
    """Maintient l'ensemble des touches actuellement enfoncées."""

    def __init__(self) -> None:
        self._pressed: set[str] = set()

    def on_key_press(self, event: tk.Event) -> None:
        self._pressed.add(event.keysym)

    def on_key_release(self, event: tk.Event) -> None:
        self._pressed.discard(event.keysym)

    def get_movements(self) -> tuple[bool, bool, bool, bool]:
        """Retourne (p1_up, p1_down, p2_up, p2_down).

        Joueur 1 (ZQSD) : 'z'/'w' = haut, 's' = bas.
        Joueur 2 : flèches 'Up'/'Down'.
        """
        p1_up = 'z' in self._pressed or 'w' in self._pressed
        p1_down = 's' in self._pressed
        p2_up = 'Up' in self._pressed
        p2_down = 'Down' in self._pressed
        return (p1_up, p1_down, p2_up, p2_down)
