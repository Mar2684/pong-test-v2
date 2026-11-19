import unittest

from pong import config
from pong.core import physics
from pong.core.entities import Ball, Net, Paddle, Position, Velocity


class TestPhysics(unittest.TestCase):
    def test_ball_wall_bounce_top(self) -> None:
        ball = Ball(position=Position(400, 5), velocity=Velocity(0, -10))
        wall = physics.check_wall_collision(ball, config.WIDTH, config.HEIGHT)
        self.assertEqual(wall, 'top')
        physics.resolve_wall_collision(ball, wall)
        self.assertGreater(ball.velocity.vy, 0)

    def test_paddle_collision_increases_speed_and_inverts_vx(self) -> None:
        paddle = Paddle(
            position=Position(
                config.WIDTH - config.PADDLE_MARGIN - config.PADDLE_WIDTH, 250
            ),
            player_id=2,
        )
        ball = Ball(position=Position(paddle.position.x - 2, 300), velocity=Velocity(100, 0))
        ball.position.x = paddle.position.x - ball.radius + 2  # chevauchement
        initial_speed = ball.speed
        result = physics.resolve_paddle_collision(ball, paddle)
        self.assertTrue(result)
        self.assertLess(ball.velocity.vx, 0)  # vx inversé
        self.assertGreater(ball.speed, initial_speed)  # accélération

    def test_net_collision_detection(self) -> None:
        net = Net()
        ball = Ball(position=Position(config.NET_X, config.HEIGHT / 2))
        self.assertTrue(physics.check_net_collision(ball, net))

    def test_ball_out_of_bounds_returns_point_event(self) -> None:
        net = Net()
        ball = Ball(position=Position(-5, 300), velocity=Velocity(-100, 0))
        result = physics.update_ball(ball, 1 / 60, [], net, config.WIDTH, config.HEIGHT)
        self.assertEqual(result, 'point_left')


if __name__ == '__main__':
    unittest.main()
