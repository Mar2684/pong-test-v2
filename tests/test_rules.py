import unittest

from pong.core.rules import MatchRules, Score
from pong.exceptions import GameError


class TestRules(unittest.TestCase):
    def test_set_won_at_11_with_2_point_gap(self) -> None:
        rules = MatchRules()
        for _ in range(9):
            rules.register_point(1)
            rules.register_point(2)
        rules.register_point(1)  # 10-9
        result = rules.register_point(1)  # 11-9
        self.assertTrue(result['set_won'])
        self.assertEqual(result['winner'], 1)
        self.assertFalse(result['match_won'])

    def test_service_alternates_every_2_points_then_every_point_at_deuce(self) -> None:
        rules = MatchRules()
        servers = []
        for i in range(4):
            result = rules.register_point(1 if i % 2 == 0 else 2)
            servers.append(result['server'])
        # serveur initial 1, alternance tous les 2 points
        self.assertEqual(servers, [1, 2, 2, 1])
        # à 10-10 : alternance à chaque point
        rules.current_score.p1 = 10
        rules.current_score.p2 = 10
        rules.points_in_set = 20
        s1 = rules.get_next_server()
        result = rules.register_point(1)  # 11-10, set non gagné (écart 1)
        s2 = result['server']
        self.assertEqual(s1, 1)
        self.assertEqual(s2, 2)

    def test_match_won_after_3_sets(self) -> None:
        rules = MatchRules()
        for _ in range(3):
            for _ in range(9):
                rules.register_point(1)
                rules.register_point(2)
            rules.register_point(1)
            rules.register_point(1)  # 11-9 : set gagné par P1
        self.assertEqual(rules.is_match_won(), 1)
        with self.assertRaises(GameError):
            rules.register_point(1)

    def test_let_flag(self) -> None:
        self.assertTrue(MatchRules(let_enabled=True).should_replay_let())
        self.assertFalse(MatchRules(let_enabled=False).should_replay_let())

    def test_score_display_and_validation(self) -> None:
        score = Score()
        score.increment(1)
        score.increment(2)
        score.increment(2)
        self.assertEqual(score.get_display(), '1-2')
        with self.assertRaises(ValueError):
            score.increment(3)


if __name__ == '__main__':
    unittest.main()
