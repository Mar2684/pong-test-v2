"""Intelligence artificielle pour le joueur 2."""

import random

from pong import config
from pong.core.entities import Ball, Paddle

_DIFFICULTY_PARAMS = {
    'easy': (0.2, 0.6, 30.0),
    'medium': (0.1, 0.85, 10.0),
    'hard': (0.05, 1.0, 0.0),
}


class PaddleAI:
    """IA poursuivant la balle avec délai de réaction, vitesse limitée et marge d'erreur."""

    def __init__(self, difficulty: str = 'medium') -> None:
        if difficulty not in _DIFFICULTY_PARAMS:
            raise ValueError(f'difficulté inconnue: {difficulty!r}')
        self.difficulty = difficulty
        self.reaction_delay, self.max_speed_factor, self.error_margin = (
            _DIFFICULTY_PARAMS[difficulty]
        )
        self._timer: float = 0.0
        self._target_y: float = config.HEIGHT / 2

    def compute_move(
        self, ball: Ball, paddle: Paddle, dt: float
    ) -> tuple[bool, bool]:
        """Retourne (up, down) : doit-on monter/descendre ce tick ?"""
        self._timer += dt
        if self._timer >= self.reaction_delay:
            self._timer = 0.0
            if ball.velocity.vx > 0:
                # la balle vient vers l'IA (à droite) : on la poursuit
                error = random.uniform(-self.error_margin, self.error_margin)
                self._target_y = ball.position.y + error
            else:
                # la balle s'éloigne : retour au centre
                self._target_y = config.HEIGHT / 2
        paddle_center = paddle.position.y + paddle.height / 2
        diff = self._target_y - paddle_center
        dead_zone = 5.0
        if diff < -dead_zone:
            return (True, False)
        if diff > dead_zone:
            return (False, True)
        return (False, False)
