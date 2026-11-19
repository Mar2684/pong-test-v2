"""Modèles de données purs (dataclasses) du jeu Pong."""

import math
from dataclasses import dataclass, field

from pong import config


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    vx: float
    vy: float


@dataclass
class Ball:
    position: Position = field(
        default_factory=lambda: Position(config.NET_X, config.HEIGHT / 2)
    )
    velocity: Velocity = field(default_factory=lambda: Velocity(0.0, 0.0))
    radius: int = config.BALL_RADIUS
    speed: float = config.BALL_SPEED_INITIAL

    def move(self, dt: float) -> None:
        """Déplace la balle selon velocity * dt."""
        self.position.x += self.velocity.vx * dt
        self.position.y += self.velocity.vy * dt

    def reset(self, server_side: int, angle: float) -> None:
        """Replace la balle au centre, dirigée vers server_side selon angle (radians)."""
        self.position = Position(config.NET_X, config.HEIGHT / 2)
        self.speed = config.BALL_SPEED_INITIAL
        self.velocity = Velocity(
            self.speed * math.cos(angle) * server_side,
            self.speed * math.sin(angle),
        )


@dataclass
class Paddle:
    position: Position = field(
        default_factory=lambda: Position(
            config.PADDLE_MARGIN, (config.HEIGHT - config.PADDLE_HEIGHT) / 2
        )
    )
    width: int = config.PADDLE_WIDTH
    height: int = config.PADDLE_HEIGHT
    speed: float = config.PADDLE_SPEED
    player_id: int = 1

    def move_up(self, dt: float) -> None:
        """Décrémente position.y de speed*dt sans descendre sous 0."""
        self.position.y = max(0.0, self.position.y - self.speed * dt)

    def move_down(self, dt: float) -> None:
        """Incrémente position.y de speed*dt sans dépasser HEIGHT - height."""
        self.position.y = min(
            config.HEIGHT - self.height, self.position.y + self.speed * dt
        )

    def get_rect(self) -> tuple[float, float, float, float]:
        """Retourne (x, y, width, height) pour les tests de collision AABB."""
        return (self.position.x, self.position.y, self.width, self.height)


@dataclass
class Net:
    x: int = config.NET_X
    y_top: float = (config.HEIGHT - config.NET_HEIGHT) / 2
    y_bottom: float = y_top + config.NET_HEIGHT
    thickness: int = config.NET_THICKNESS

    def get_rect(self) -> tuple[float, float, float, float]:
        """Retourne la boîte englobante du filet (x, y, width, height)."""
        return (
            self.x - self.thickness / 2,
            self.y_top,
            self.thickness,
            self.y_bottom - self.y_top,
        )
