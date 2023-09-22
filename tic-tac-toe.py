"""Adapted from tutorial : https://realpython.com/tic-tac-toe-python/"""

import tkinter as tk
from itertools import cycle
from tkinter import font, simpledialog, messagebox
from typing import NamedTuple


class Player(NamedTuple):
    name: str
    label: str 
    color: str



class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3
player1_name = simpledialog.askstring("Player Names", "Please Enter Player 1's Name:")
player2_name = simpledialog.askstring("Player Names", "Please Enter Player 2's Name:")

if player1_name == None:
    player1_name = "Player 1"
if player2_name == None:
    player2_name = "Player 2"

DEFAULT_PLAYERS = (
    Player(name = player1_name.title(), label="X", color="pink"),
    Player(name = player2_name.title(), label="O", color="purple")
)


class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows =[
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)

    def toggle_player(self):
        self.current_player = next(self._players)

    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)

        self._has_winner = False
        self.winner_combo = []


class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic_Tac_Toe_Game")
        self._cells = {}
        self._game = game
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()


    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(
            label="Play Again",
            command=self.reset_board
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _create_board_display(self):
        display_frame = tk.Frame(master=self, bg="white")
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            bg="white",
            text=f"{self._game.current_player.name}'s turn",
            font=font.Font(size=28, weight="normal", family='Irene Florentina'),
        )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self, bg="white")
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold", family='Irene Florentina'),
                    bg="white",
                    fg="black",
                    width=3,
                    height=1,
                    highlightbackground="lightblue",
                    relief=tk.SOLID
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(
                    row=row,
                    column=col,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )

    def play(self, event):
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="Tied game!", color="red")
                self.ask_reset()
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'{self._game.current_player.name} won!'
                color = self._game.current_player.color
                self._update_display(msg, color)
                self.ask_reset()
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.name}'s turn"
                self._update_display(msg)

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        self._game.reset_game()
        self._update_display(msg=f"{self._game.current_player.name}'s turn")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")
    
    def ask_reset(self):
        if messagebox.askyesno("Reset", "Do you want to play again?"):
            self.reset_board()
        else:
            quit()


def main():
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()


if __name__ == "__main__":
    main()
