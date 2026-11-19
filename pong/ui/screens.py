"""Gestion des écrans (menu, jeu, fin) comme couches d'UI."""

import tkinter as tk

from pong.ui.renderer import Renderer


class ScreenManager:
    """Dessine les écrans titre/fin et traduit les clics en actions."""

    def __init__(self, app: 'object', renderer: Renderer) -> None:
        self.app = app
        self.renderer = renderer
        # action -> (x0, y0, x1, y1) pour l'écran courant
        self._buttons: dict[str, dict[str, tuple[int, int, int, int]]] = {}
        self._end_callbacks: tuple = (lambda: None, lambda: None)

    def _add_button(
        self, screen: str, action: str, cx: int, cy: int, w: int = 260, h: int = 50
    ) -> tuple[int, int, int, int]:
        rect = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)
        self._buttons.setdefault(screen, {})[action] = rect
        return rect

    def _draw_button(self, rect: tuple[int, int, int, int], label: str) -> None:
        x0, y0, x1, y1 = rect
        self.renderer.canvas.create_rectangle(
            x0, y0, x1, y1, outline='#FFFFFF', width=2, fill='#222222'
        )
        self.renderer.canvas.create_text(
            (x0 + x1) / 2,
            (y0 + y1) / 2,
            text=label,
            fill='#FFFFFF',
            font=('Helvetica', 16, 'bold'),
        )

    def show_menu(self) -> None:
        """Dessine l'écran titre avec les options de partie."""
        canvas = self.renderer.canvas
        self.renderer.clear()
        canvas.create_rectangle(
            0, 0, self.renderer.width, self.renderer.height, fill='#000000', outline=''
        )
        canvas.create_text(
            self.renderer.width / 2,
            150,
            text='PONG',
            fill='#FFFFFF',
            font=('Helvetica', 64, 'bold'),
        )
        canvas.create_text(
            self.renderer.width / 2,
            220,
            text='Jeu de ping-pong 2D — 11 points, 3 sets',
            fill='#AAAAAA',
            font=('Helvetica', 14),
        )
        self._buttons['menu'] = {}
        self._draw_button(
            self._add_button('menu', 'start_2p', 400, 320), '1. 2 Joueurs'
        )
        self._draw_button(
            self._add_button('menu', 'start_ai', 400, 390), '2. Contre IA'
        )
        self._draw_button(self._add_button('menu', 'quit', 400, 460), '3. Quitter')

    def show_game(self) -> None:
        """Efface le canvas pour le rendu jeu."""
        self.renderer.clear()
        self._buttons['game'] = {}

    def show_end(self, winner: int, on_replay: 'callable', on_menu: 'callable') -> None:
        """Dessine l'écran de victoire avec les boutons Rejouer / Menu."""
        self._end_callbacks = (on_replay, on_menu)
        canvas = self.renderer.canvas
        canvas.create_rectangle(
            0, 0, self.renderer.width, self.renderer.height, fill='#000000', outline=''
        )
        canvas.create_text(
            self.renderer.width / 2,
            200,
            text=f'VICTOIRE JOUEUR {winner}',
            fill='#FFFFFF',
            font=('Helvetica', 40, 'bold'),
        )
        self._buttons['end'] = {}
        self._draw_button(
            self._add_button('end', 'replay', 400, 340), 'Rejouer'
        )
        self._draw_button(self._add_button('end', 'menu', 400, 410), 'Menu')

    def handle_click(self, x: int, y: int, current_state: str) -> 'str | None':
        """Retourne l'action choisie selon les coordonnées du clic, None sinon."""
        for action, (x0, y0, x1, y1) in self._buttons.get(current_state, {}).items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                return action
        return None
