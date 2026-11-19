"""Détection et résolution des collisions (fonctions pures)."""

import math

from pong import config
from pong.core.entities import Ball, Net, Paddle
from pong.exceptions import GameError

_MAX_BOUNCE_ANGLE = math.radians(60.0)  # angle max depuis le centre de la raquette


def check_aabb_collision(
    rect: tuple[float, float, float, float],
    circle_x: float,
    circle_y: float,
    radius: float,
) -> bool:
    """Retourne True si le cercle (balle) intersecte le rectangle AABB."""
    x, y, w, h = rect
    closest_x = max(x, min(circle_x, x + w))
    closest_y = max(y, min(circle_y, y + h))
    dx = circle_x - closest_x
    dy = circle_y - closest_y
    return (dx * dx + dy * dy) <= radius * radius


def resolve_paddle_collision(ball: Ball, paddle: Paddle) -> bool:
    """Rebond raquette : inverse vx, accélère, ajuste vy selon le point de contact."""
    rect = paddle.get_rect()
    if not check_aabb_collision(
        rect, ball.position.x, ball.position.y, ball.radius
    ):
        return False
    paddle_center_x = paddle.position.x + paddle.width / 2
    if paddle_center_x < ball.position.x:
        # raquette à gauche : la balle doit venir vers la gauche (vx < 0)
        moving_toward = ball.velocity.vx < 0
        direction = 1.0  # après rebond, vers la droite
    else:
        # raquette à droite : la balle doit venir vers la droite (vx > 0)
        moving_toward = ball.velocity.vx > 0
        direction = -1.0
    if not moving_toward:
        return False
    ball.speed *= config.BALL_SPEED_INCREMENT
    rel = (ball.position.y - (paddle.position.y + paddle.height / 2)) / (
        paddle.height / 2
    )
    rel = max(-1.0, min(1.0, rel))
    angle = rel * _MAX_BOUNCE_ANGLE
    ball.velocity.vx = direction * ball.speed * math.cos(angle)
    ball.velocity.vy = ball.speed * math.sin(angle)
    # replace la balle hors de la raquette pour éviter les collisions répétées
    if direction > 0:
        ball.position.x = paddle.position.x + paddle.width + ball.radius
    else:
        ball.position.x = paddle.position.x - ball.radius
    return True


def check_wall_collision(ball: Ball, width: int, height: int) -> str | None:
    """Retourne 'top'/'bottom'/'left'/'right' si la balle touche un mur, sinon None."""
    if ball.position.y - ball.radius < 0:
        return 'top'
    if ball.position.y + ball.radius > height:
        return 'bottom'
    if ball.position.x - ball.radius < 0:
        return 'left'
    if ball.position.x + ball.radius > width:
        return 'right'
    return None


def resolve_wall_collision(ball: Ball, wall: str) -> None:
    """Inverse la composante de vélocité correspondant au mur touché."""
    if wall in ('top', 'bottom'):
        ball.velocity.vy = -ball.velocity.vy
    elif wall in ('left', 'right'):
        ball.velocity.vx = -ball.velocity.vx


def check_net_collision(ball: Ball, net: Net) -> bool:
    """Retourne True si la balle chevauche le rectangle du filet."""
    return check_aabb_collision(
        net.get_rect(), ball.position.x, ball.position.y, ball.radius
    )


def update_ball(
    ball: Ball,
    dt: float,
    paddles: list[Paddle],
    net: Net,
    width: int,
    height: int,
) -> str | None:
    """Intègre le mouvement et résout collisions murs/raquettes/filet.

    Retourne 'point_left' si x < 0, 'point_right' si x > width, 'let' si le
    filet est touché, None sinon. Lève GameError si dt <= 0.
    """
    if dt <= 0:
        raise GameError('dt doit être strictement positif')
    # la balle servie démarre au centre, dans le filet : on ne doit pas lever
    # de let tant qu'elle n'a pas pénétré dans le filet depuis l'extérieur
    was_on_net = check_net_collision(ball, net)
    ball.move(dt)
    if ball.position.x < 0:
        return 'point_left'
    if ball.position.x > width:
        return 'point_right'
    wall = check_wall_collision(ball, width, height)
    if wall is not None:
        resolve_wall_collision(ball, wall)
    for paddle in paddles:
        resolve_paddle_collision(ball, paddle)
    if check_net_collision(ball, net) and not was_on_net:
        return 'let'
    return None
