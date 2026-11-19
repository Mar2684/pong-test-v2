"""Dessin sur le canvas tkinter."""

import tkinter as tk

from pong import config
from pong.core.entities import Ball, Net, Paddle
from pong.core.game_state import GameState
from pong.core.rules import MatchRules

_COLOR_P1 = '#00FFFF'  # cyan
_COLOR_P2 = '#FF00FF'  # magenta
_COLOR_BALL = '#FFFFFF'
_COLOR_NET = '#FFFFFF'
_COLOR_BG = '#000000'
_COLOR_TEXT = '#FFFFFF'


class Renderer:
    """Dessine l'état du jeu sur le canvas."""

    def __init__(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas
        self.width: int = config.WIDTH
        self.height: int = config.HEIGHT

    def clear(self) -> None:
        self.canvas.delete('all')

    def draw(self, state: GameState) -> None:
        """Efface puis redessine fond, filet, raquettes, balle, score et messages."""
        self.clear()
        self.canvas.create_rectangle(
            0, 0, self.width, self.height, fill=_COLOR_BG, outline=''
        )
        self._draw_net(state.net)
        self._draw_paddle(state.paddle1, _COLOR_P1)
        self._draw_paddle(state.paddle2, _COLOR_P2)
        self._draw_ball(state.ball)
        self._draw_score(state.rules)
        if state.message_timer > 0 and state.message:
            self.canvas.create_text(
                self.width / 2,
                self.height / 2 - 80,
                text=state.message,
                fill=_COLOR_TEXT,
                font=('Helvetica', 32, 'bold'),
            )

    def _draw_paddle(self, paddle: Paddle, color: str) -> None:
        x, y, w, h = paddle.get_rect()
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline='')

    def _draw_ball(self, ball: Ball) -> None:
        x, y, r = ball.position.x, ball.position.y, ball.radius
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill=_COLOR_BALL, outline=''
        )

    def _draw_net(self, net: Net) -> None:
        x, y, w, h = net.get_rect()
        self.canvas.create_rectangle(
            x, y, x + w, y + h, fill=_COLOR_NET, outline='', dash=(6, 6)
        )

    def _draw_score(self, rules: MatchRules) -> None:
        score = rules.current_score.get_display()
        self.canvas.create_text(
            self.width / 2,
            30,
            text=score,
            fill=_COLOR_TEXT,
            font=('Helvetica', 28, 'bold'),
        )
        # indicateur de serveur '●' à côté du score du serveur
        p1, p2 = rules.current_score.p1, rules.current_score.p2
        if rules.server == 1:
            self.canvas.create_text(
                self.width / 2 - 60 - len(str(p1)) * 8,
                30,
                text='●',
                fill=_COLOR_P1,
                font=('Helvetica', 16, 'bold'),
            )
        else:
            self.canvas.create_text(
                self.width / 2 + 60 + len(str(p2)) * 8,
                30,
                text='●',
                fill=_COLOR_P2,
                font=('Helvetica', 16, 'bold'),
            )
