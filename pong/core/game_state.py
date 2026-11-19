"""Orchestrateur central de l'état du jeu (machine à états)."""

import random

from pong import config
from pong.ai import PaddleAI
from pong.core import physics
from pong.core.entities import Ball, Net, Paddle, Position
from pong.core.rules import MatchRules
from pong.exceptions import GameError


class State:
    """États internes possibles de la machine à états."""

    MENU = 'menu'
    SERVING = 'serving'
    PLAYING = 'playing'
    POINT_SCORED = 'point_scored'
    SET_WON = 'set_won'
    MATCH_WON = 'match_won'


_SERVE_DELAY: float = 1.0
_POINT_DELAY: float = 1.0
_SET_DELAY: float = 2.0
_LET_MESSAGE_DELAY: float = 0.8
_SERVICE_ANGLE_RANGE: float = 0.4


class GameState:
    """Machine à états du jeu : menu -> serving -> playing -> point_scored/set_won/match_won."""

    def __init__(self) -> None:
        self.ball = Ball()
        self.paddle1 = Paddle(
            position=Position(
                config.PADDLE_MARGIN, (config.HEIGHT - config.PADDLE_HEIGHT) / 2
            ),
            player_id=1,
        )
        self.paddle2 = Paddle(
            position=Position(
                config.WIDTH - config.PADDLE_MARGIN - config.PADDLE_WIDTH,
                (config.HEIGHT - config.PADDLE_HEIGHT) / 2,
            ),
            player_id=2,
        )
        self.net = Net()
        self.rules = MatchRules()
        self.state: str = State.MENU
        self.ai_enabled: bool = False
        self.ai: PaddleAI | None = None
        self.last_scorer: int = 0
        self.message_timer: float = 0.0
        self.message: str = ''
        self.serve_timer: float = 0.0
        self.point_timer: float = 0.0

    def start_match(self, vs_ai: bool = False, ai_difficulty: str = 'medium') -> None:
        """Réinitialise le match et passe à l'état 'serving'."""
        self.rules = MatchRules()
        self.ball = Ball()
        self.paddle1 = Paddle(
            position=Position(
                config.PADDLE_MARGIN, (config.HEIGHT - config.PADDLE_HEIGHT) / 2
            ),
            player_id=1,
        )
        self.paddle2 = Paddle(
            position=Position(
                config.WIDTH - config.PADDLE_MARGIN - config.PADDLE_WIDTH,
                (config.HEIGHT - config.PADDLE_HEIGHT) / 2,
            ),
            player_id=2,
        )
        self.ai_enabled = vs_ai
        self.ai = PaddleAI(ai_difficulty) if vs_ai else None
        self.last_scorer = 0
        self.message = ''
        self.message_timer = 0.0
        self.state = State.SERVING
        self.reset_for_service()

    def reset_for_service(self) -> None:
        """Replace la balle pour le service du serveur actuel (angle aléatoire)."""
        angle = random.uniform(-_SERVICE_ANGLE_RANGE, _SERVICE_ANGLE_RANGE)
        self.ball.reset(self.rules.server, angle)
        self.serve_timer = _SERVE_DELAY

    def update(
        self,
        dt: float,
        p1_up: bool = False,
        p1_down: bool = False,
        p2_up: bool = False,
        p2_down: bool = False,
    ) -> list[str]:
        """Avance la machine à états d'un tick. Retourne les événements survenus."""
        if dt <= 0:
            raise GameError('dt doit être strictement positif')
        events: list[str] = []

        # --- mouvements des raquettes ---
        if p1_up:
            self.paddle1.move_up(dt)
        if p1_down:
            self.paddle1.move_down(dt)
        if self.ai_enabled and self.ai is not None:
            up, down = self.ai.compute_move(self.ball, self.paddle2, dt)
            if up:
                self.paddle2.move_up(dt * self.ai.max_speed_factor)
            if down:
                self.paddle2.move_down(dt * self.ai.max_speed_factor)
        else:
            if p2_up:
                self.paddle2.move_up(dt)
            if p2_down:
                self.paddle2.move_down(dt)

        if self.message_timer > 0:
            self.message_timer -= dt

        # --- machine à états ---
        if self.state == State.SERVING:
            self.serve_timer -= dt
            if self.serve_timer <= 0:
                self.state = State.PLAYING
        elif self.state == State.PLAYING:
            result = physics.update_ball(
                self.ball,
                dt,
                [self.paddle1, self.paddle2],
                self.net,
                config.WIDTH,
                config.HEIGHT,
            )
            if result == 'let':
                events.append('let')
                self.message = 'LET'
                self.message_timer = _LET_MESSAGE_DELAY
                if self.rules.should_replay_let():
                    self.reset_for_service()
                    self.state = State.SERVING
            elif result in ('point_left', 'point_right'):
                scorer = 2 if result == 'point_left' else 1
                events.append('point_p1' if scorer == 1 else 'point_p2')
                self.last_scorer = scorer
                self.reset_for_service()
                outcome = self.rules.register_point(scorer)
                if outcome.get('set_won'):
                    events.append('set_won')
                    self.message = 'SET GAGNÉ'
                    self.message_timer = _SET_DELAY
                    self.point_timer = _SET_DELAY
                    if outcome.get('match_won'):
                        events.append('match_won')
                        self.message = 'MATCH GAGNÉ'
                        self.state = State.MATCH_WON
                    else:
                        self.state = State.SET_WON
                else:
                    self.state = State.POINT_SCORED
                    self.point_timer = _POINT_DELAY
        elif self.state == State.POINT_SCORED:
            self.point_timer -= dt
            if self.point_timer <= 0:
                self.state = State.SERVING
                self.serve_timer = _SERVE_DELAY
        elif self.state == State.SET_WON:
            self.point_timer -= dt
            if self.point_timer <= 0:
                self.state = State.SERVING
                self.serve_timer = _SERVE_DELAY
        return events

    def get_display_state(self) -> dict:
        """Retourne un dictionnaire sérialisable pour le renderer."""
        return {
            'ball': {
                'x': self.ball.position.x,
                'y': self.ball.position.y,
                'radius': self.ball.radius,
            },
            'paddles': [
                {
                    'x': p.position.x,
                    'y': p.position.y,
                    'width': p.width,
                    'height': p.height,
                    'player_id': p.player_id,
                }
                for p in (self.paddle1, self.paddle2)
            ],
            'score': self.rules.current_score.get_display(),
            'server': self.rules.server,
            'state': self.state,
        }
