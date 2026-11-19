"""Application tkinter principale et boucle de jeu."""

import time
import tkinter as tk

from pong import config
from pong.audio import SoundEngine
from pong.core.game_state import GameState
from pong.ui.input import InputHandler
from pong.ui.renderer import Renderer
from pong.ui.screens import ScreenManager


class App:
    """Fenêtre 800x600, boucle fixed timestep via tk.after(16)."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title('Pong')
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            self.root, width=config.WIDTH, height=config.HEIGHT, bg='#000000'
        )
        self.canvas.pack()
        self.state = GameState()
        self.input_handler = InputHandler()
        self.renderer = Renderer(self.canvas)
        self.screens = ScreenManager(self, self.renderer)
        self.sound = SoundEngine()
        self.sound.load_sounds()
        self.last_time: float = time.time()
        self.running: bool = True
        self.current_screen: str = 'menu'
        self.root.bind('<KeyPress>', self.input_handler.on_key_press)
        self.root.bind('<KeyRelease>', self.input_handler.on_key_release)
        self.root.bind('<Button-1>', self._handle_menu_click)
        self.root.protocol('WM_DELETE_WINDOW', self.on_quit)
        self.screens.show_menu()
        self.root.after(16, self.game_loop)

    def run(self) -> None:
        """Lance la boucle principale tkinter."""
        self.root.mainloop()

    def game_loop(self) -> None:
        """Un tick de jeu : dt réel (limité à 0.05s), entrées, update, sons, rendu."""
        if not self.running:
            return
        now = time.time()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now
        if self.current_screen == 'game':
            movements = self.input_handler.get_movements()
            events = self.state.update(dt, *movements)
            for event in events:
                if event in ('point_p1', 'point_p2'):
                    self.sound.play('point')
                elif event == 'let':
                    self.sound.play('let')
            if 'match_won' in events:
                winner = self.state.rules.is_match_won() or self.state.last_scorer
                self.current_screen = 'end'
                self.screens.show_end(winner, self._on_replay, self._on_menu)
            self.renderer.draw(self.state)
        self.root.after(16, self.game_loop)

    def on_quit(self) -> None:
        """Arrête la boucle et détruit la fenêtre."""
        self.running = False
        self.root.destroy()

    def _handle_menu_click(self, event: tk.Event) -> None:
        """Délègue le clic à screens.handle_click et démarre la partie si demandé."""
        action = self.screens.handle_click(event.x, event.y, self.current_screen)
        if action == 'start_2p':
            self.state.start_match(vs_ai=False)
            self.current_screen = 'game'
            self.screens.show_game()
        elif action == 'start_ai':
            self.state.start_match(vs_ai=True)
            self.current_screen = 'game'
            self.screens.show_game()
        elif action == 'quit':
            self.on_quit()
        elif action == 'replay':
            self._on_replay()
        elif action == 'menu':
            self._on_menu()

    def _on_replay(self) -> None:
        self.state.start_match(vs_ai=self.state.ai_enabled)
        self.current_screen = 'game'
        self.screens.show_game()

    def _on_menu(self) -> None:
        self.current_screen = 'menu'
        self.state.state = 'menu'
        self.screens.show_menu()
