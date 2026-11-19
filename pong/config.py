"""Constantes globales du jeu Pong."""

WIDTH: int = 800
HEIGHT: int = 600
FPS: int = 60
DT: float = 1.0 / 60.0

PADDLE_WIDTH: int = 15
PADDLE_HEIGHT: int = 100
PADDLE_SPEED: float = 400.0  # pixels/s
PADDLE_MARGIN: int = 50  # distance au bord

BALL_RADIUS: int = 8
BALL_SPEED_INITIAL: float = 300.0
BALL_SPEED_INCREMENT: float = 1.05  # facteur d'accélération à chaque rebond raquette

NET_X: int = 400
NET_HEIGHT: int = 100
NET_THICKNESS: int = 6

POINTS_TO_WIN_SET: int = 11
SETS_TO_WIN_MATCH: int = 3
SERVICE_POINTS_ROTATION: int = 2  # alterne tous les 2 points sauf à 10-10
