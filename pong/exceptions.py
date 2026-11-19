"""Exceptions métier du jeu Pong."""


class GameError(Exception):
    """Levée pour les états de jeu invalides (ex: match déjà terminé)."""
