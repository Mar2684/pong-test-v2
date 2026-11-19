"""Gestion du score, des sets, du service et des lets."""

from dataclasses import dataclass, field

from pong import config
from pong.exceptions import GameError


@dataclass
class Score:
    p1: int = 0
    p2: int = 0

    def increment(self, player: int) -> None:
        """Incrémente le score du joueur 1 ou 2. ValueError si player invalide."""
        if player == 1:
            self.p1 += 1
        elif player == 2:
            self.p2 += 1
        else:
            raise ValueError(f'player doit être 1 ou 2, reçu {player!r}')

    def get_display(self) -> str:
        """Retourne le score au format '11-7'."""
        return f'{self.p1}-{self.p2}'

    def is_set_won(self, points_to_win: int) -> int | None:
        """Retourne 1 ou 2 si un joueur a points_to_win avec 2 points d'écart."""
        if self.p1 >= points_to_win and self.p1 - self.p2 >= 2:
            return 1
        if self.p2 >= points_to_win and self.p2 - self.p1 >= 2:
            return 2
        return None

    def reset(self) -> None:
        self.p1 = 0
        self.p2 = 0


@dataclass
class MatchRules:
    points_to_win: int = config.POINTS_TO_WIN_SET
    sets_to_win: int = config.SETS_TO_WIN_MATCH
    current_set: int = 1
    sets_won: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0})
    current_score: Score = field(default_factory=Score)
    server: int = 1
    points_in_set: int = 0
    let_enabled: bool = True

    def register_point(self, scorer: int) -> dict[str, bool | int]:
        """Enregistre un point et retourne l'état resulting (set/match won, serveur)."""
        if self.is_match_won() is not None:
            raise GameError('le match est déjà terminé')
        if scorer not in (1, 2):
            raise ValueError(f'scorer doit être 1 ou 2, reçu {scorer!r}')
        self.current_score.increment(scorer)
        self.points_in_set += 1
        winner = self.current_score.is_set_won(self.points_to_win)
        if winner is not None:
            self.sets_won[winner] += 1
            self.current_set += 1
            match_won = self.is_match_won() is not None
            self.current_score.reset()
            self.points_in_set = 0
            self.server = self.get_next_server()
            return {
                'set_won': True,
                'match_won': match_won,
                'winner': winner,
            }
        self.server = self.get_next_server()
        return {'set_won': False, 'match_won': False, 'server': self.server}

    def get_next_server(self) -> int:
        """Alterne tous les SERVICE_POINTS_ROTATION points, ou à chaque point à 10-10."""
        if (
            self.current_score.p1 >= self.points_to_win - 1
            and self.current_score.p2 >= self.points_to_win - 1
        ):
            # égalité (deuce) : service alterné à chaque point
            return 1 if self.points_in_set % 2 == 0 else 2
        return (
            1
            if (self.points_in_set // config.SERVICE_POINTS_ROTATION) % 2 == 0
            else 2
        )

    def is_match_won(self) -> int | None:
        """Retourne le joueur gagnant si sets_won atteint sets_to_win."""
        for player in (1, 2):
            if self.sets_won[player] >= self.sets_to_win:
                return player
        return None

    def should_replay_let(self) -> bool:
        """Retourne True si let_enabled est True."""
        return self.let_enabled
