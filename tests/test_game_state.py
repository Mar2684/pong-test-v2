import unittest

from pong import config
from pong.core.entities import Position, Velocity
from pong.core.game_state import GameState, State
from pong.exceptions import GameError


def _reach_playing(gs: GameState) -> None:
    """Fait avancer la machine à états jusqu'à l'état 'playing'."""
    for _ in range(200):
        gs.update(config.DT)
        if gs.state == State.PLAYING:
            return
    raise AssertionError('état playing non atteint')


class TestGameState(unittest.TestCase):
    def test_update_moves_paddles_with_input(self) -> None:
        gs = GameState()
        gs.start_match()
        y0 = gs.paddle1.position.y
        gs.update(0.1, p1_up=True)
        self.assertLess(gs.paddle1.position.y, y0)

    def test_point_scored_event_when_ball_out(self) -> None:
        gs = GameState()
        gs.start_match()
        _reach_playing(gs)
        gs.ball.position = Position(config.WIDTH - 5, 300)
        gs.ball.velocity = Velocity(600, 0)
        events = gs.update(config.DT)
        self.assertIn('point_p1', events)
        self.assertEqual(gs.rules.current_score.p1, 1)

    def test_let_resets_to_serving(self) -> None:
        gs = GameState()
        gs.start_match()
        _reach_playing(gs)
        gs.ball.position = Position(config.NET_X - 12, 300)
        gs.ball.velocity = Velocity(100, 0)  # pénètre dans le filet à ce tick
        events = gs.update(config.DT)
        self.assertIn('let', events)
        self.assertEqual(gs.state, State.SERVING)

    def test_ai_mode_activates_paddle2(self) -> None:
        gs = GameState()
        gs.start_match(vs_ai=True)
        _reach_playing(gs)
        gs.ball.position = Position(600, 100)
        gs.ball.velocity = Velocity(300, 0)
        y0 = gs.paddle2.position.y
        moved = False
        for _ in range(60):
            gs.update(config.DT)
            if gs.paddle2.position.y != y0:
                moved = True
                break
        self.assertTrue(moved, 'la raquette IA n a pas bougé')

    def test_update_rejects_non_positive_dt(self) -> None:
        gs = GameState()
        gs.start_match()
        with self.assertRaises(GameError):
            gs.update(0)

    def test_display_state_is_serializable(self) -> None:
        gs = GameState()
        gs.start_match()
        d = gs.get_display_state()
        self.assertIn('ball', d)
        self.assertEqual(len(d['paddles']), 2)
        self.assertEqual(d['score'], '0-0')
        self.assertEqual(d['server'], 1)
        self.assertEqual(d['state'], State.SERVING)


if __name__ == '__main__':
    unittest.main()
