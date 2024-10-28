import os
from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Any, Generator, Optional, Type, Iterable
from framework.board import Position, Board
import PySimpleGUI as sg

from framework.gui import BoardGUI


Actions = Enum("Actions", "N W S E")
Directions = {
    Actions.N: Position(1, 0),
    Actions.E: Position(0, -1),
    Actions.S: Position(-1, 0),
    Actions.W: Position(0, 1),
}

@dataclass(frozen=True)
class State:
    position: Position


LabyrinthFields = Enum("LabyrinthFields", "Empty Wall M N O P I J K L E F G H A B C D")
LABYRINTH_TXT = "home_assign.txt"
TILE_DIR = "../tiles"
image_paths = {
    LabyrinthFields.Empty: os.path.join(TILE_DIR, "blank_scaled.png"),
}
class LabyrinthBoard(Board):
    def __init__(self, path: str):
        self.load(path)

    def load(self, path: str) -> None:
        load_dict = {
            " ": LabyrinthFields.Empty,
            "W": LabyrinthFields.Wall,
            "M": LabyrinthFields.M,
            "N": LabyrinthFields.N,
            "O": LabyrinthFields.O,
            "P": LabyrinthFields.P,
            "I": LabyrinthFields.I,
            "J": LabyrinthFields.J,
            "K": LabyrinthFields.K,
            "L": LabyrinthFields.L,
            "E": LabyrinthFields.E,
            "F": LabyrinthFields.F,
            "G": LabyrinthFields.G,
            "H": LabyrinthFields.H,
            "A": LabyrinthFields.A,
            "B": LabyrinthFields.B,
            "C": LabyrinthFields.C,
            "D": LabyrinthFields.D,
        }
        with open(path) as f:
            self.board = [[load_dict.get(ch, LabyrinthFields.Empty) for ch in line.strip()] for line in f]
        for row in self.board:
            assert len(row) == len(self.board[0]), "The board should be rectangular!"
        self.m = len(self.board)
        self.n = len(self.board[0])
        self.walls = [

        ]
class LabyrinthGUI(BoardGUI):
    CELL_SIZE = (30, 30)
    WALL_COLOR = ("black", "black")
    EMPTY_COLOR = ("white", "white")
    def __init__(self, board: LabyrinthBoard, draw_dict: dict):
        super().__init__(board, draw_dict)
        self.board = board
        self.draw_dict = draw_dict
        self.board_layout = [
            [
                sg.Button(
                    "",
                    image_filename=image_paths[LabyrinthFields.Empty],
                    pad=(0, 0),
                    key=(i, j),
                    button_color=("black", "white"),
                    font=("Helvetica", 8),
                    image_size=self.get_wall_size(i, j),
                    border_width=0

                )
                for i in range(board.n)
            ]
            for j in range(board.m)
        ]

    def is_wall(self, row, col):
        return self.board.board[row][col] == LabyrinthFields.Wall

    def is_empty(self, row, col):
        return self.board.board[row][col] == LabyrinthFields.Empty

    def get_wall_size(self, row, col):
        if (row % 2 == 0) and (col % 2 == 0):
            return 1, 1
        elif (row % 2 == 0) and (col % 2 != 0):
            return 1, 30
        elif (row % 2 != 0) and (col % 2 == 0):
            return 30, 1
        else:
            return self.CELL_SIZE

    def update_nodes(self, expanded_nodes: Iterable[State]) -> None:
        for state in expanded_nodes:
            pos = state.position
            field_type = self.board.board[pos.row][pos.col]
            label, (text_color, bg_color), image = labyrinth_draw_dict[field_type]

            if image:
                self.board_layout[pos.row][pos.col].Update(
                    "",
                    button_color=(text_color, bg_color),
                    image_filename=image,
                    image_size=self.CELL_SIZE,
                    image_subsample=1,
                )
            else:
                self.board_layout[pos.row][pos.col].Update(
                    label, button_color=(text_color, bg_color)
                )
class LabyrinthSearchProblem(ABC):
    def __init__(self):
        self.board = board
        self.start = self.find_position(LabyrinthFields.M)
        self.goal = self.find_position(LabyrinthFields.D)

    def find_position(self, field_type: LabyrinthFields) -> Position:
        for row in range(self.board.m):
            for col in range(self.board.n):
                if self.board.board[row][col] == field_type:
                    return Position(row, col)
        raise ValueError(f"Field type {field_type} not found on the board.")

    def start_state(self) -> State:
        return State(self.start)

    def is_goal_state(self, state: State) -> bool:
        return state.position == self.goal

    def next_states(self, state: State) -> set[State]:
        next_positions = set()
        for action, direction in Directions.items():
            next_pos = state.position + direction
            if 0 <= next_pos.row < self.board.m and 0 <= next_pos.col < self.board.n:
                cell_type = self.board.board[next_pos.row][next_pos.col]
                if cell_type not in {LabyrinthFields.Wall, LabyrinthFields.Empty}:
                    next_positions.add(State(next_pos))
        return next_positions

def backtrack(
    problem: LabyrinthSearchProblem, step_by_step: bool = False
) -> Optional[Generator[State, None, None]]:
    start_state = problem.start_state()
    path: list[State] = []
    def backtrack_recursive(current: State) -> Optional[list[State]]:
        if problem.is_goal_state(current):
            return path
        for next_state in problem.next_states(current):
            path.append(next_state)
            result = backtrack_recursive(next_state)
            if result:
                return [next_state] + result
        return None

    result = backtrack_recursive(start_state)
    if result:
        return (r for r in path) if step_by_step else (r for r in result)
    else:
        return None


labyrinth_draw_dict = {
    LabyrinthFields.Empty: (" ", ("white", "white"), None),
    LabyrinthFields.Wall: ("W", ("black", "black"), None),
    LabyrinthFields.M: ("M", ("black", "white"), None),
    LabyrinthFields.N: ("N", ("black", "white"), None),
    LabyrinthFields.O: ("O", ("black", "white"), None),
    LabyrinthFields.P: ("P", ("black", "white"), None),
    LabyrinthFields.I: ("I", ("black", "white"), None),
    LabyrinthFields.J: ("J", ("black", "white"), None),
    LabyrinthFields.K: ("K", ("black", "white"), None),
    LabyrinthFields.L: ("L", ("black", "white"), None),
    LabyrinthFields.E: ("E", ("black", "white"), None),
    LabyrinthFields.F: ("F", ("black", "white"), None),
    LabyrinthFields.G: ("G", ("black", "white"), None),
    LabyrinthFields.H: ("H", ("black", "white"), None),
    LabyrinthFields.A: ("A", ("black", "white"), None),
    LabyrinthFields.B: ("B", ("black", "white"), None),
    LabyrinthFields.C: ("C", ("black", "white"), None),
    LabyrinthFields.D: ("D", ("black", "white"), None),
}


board = LabyrinthBoard(LABYRINTH_TXT)
board_gui = LabyrinthGUI(board, labyrinth_draw_dict)


def create_window(board_gui):

    layout = [
        [sg.Column(board_gui.board_layout)],
        [
            sg.Frame(
                "Algorithm settings",
                [
                    [
                        sg.T("Algorithm: ", size=(12, 1)),
                        sg.Combo(
                            [
                                "Backtrack - just the solution",
                                "Backtrack - step by step",
                            ],
                            key="algorithm",
                            readonly=True,
                            default_value="Backtrack - just the solution",
                        ),
                    ],
                    [sg.Button("Change", key="change_algorithm")],
                ],
            ),
            sg.Frame(
                "Problem settings",
                [
                    [
                        sg.T("Labyrinth: "),
                        sg.Combo(
                            LABYRINTH_TXT,
                            key="labyrinth",
                            readonly=True,
                            default_value=LABYRINTH_TXT)
                    ],
                    [
                        sg.T("Board size: ", size=(12, 1)),
                        sg.Combo(
                            ["9x9"],
                            key="board_size",
                            readonly=True,
                            default_value="9x9"
                        ),
                    ],
                    [sg.Button("Change", key="change_problem")],
                ],
            ),
        ],
        [sg.T("Steps: "), sg.T("0", key="steps", size=(7, 1), justification="right")],
        [sg.Button("Restart"), sg.Button("Step"), sg.Button("Go!"), sg.Button("Exit")],
    ]

    window = sg.Window(
        "N queens problem",
        layout,
        default_button_element_size=(10, 1),
        auto_size_buttons=False,
        location=(0,0)
    )
    return window

window = create_window(board_gui)

starting = True
go = False
steps = 0

algorithms = {
    "Backtrack - step by step": partial(backtrack, step_by_step=True),
    "Backtrack - just the solution": backtrack,
}

while True:  # Event Loop
    event, values = window.Read(0)
    if event is None or event == "Exit" or event == sg.WIN_CLOSED:
        break
    window.Element("Go!").Update(text="Stop!" if go else "Go!")
    if event == "change_algorithm" or starting:
        algorithm: Any = algorithms[values["algorithm"]]
        board_gui.board = board
        #path = algorithm(algorithm[0])
        steps = 0
        starting = False
        stepping = True
    if event == "Restart":
        board_gui.board = board
        #path = algorithm()
        steps = 0
        stepping = True
    if (event == "Step" or go or stepping): # and path:
        try:
            #state = next(path)
            steps += 1
            window.Element("steps").Update(f"{steps}")
        except StopIteration:
            pass
        board = board# queens_problem._to_drawable(state)
        board_gui.board = board
        board_gui.update()
        stepping = False
    if event == "Go!":
        go = not go

window.Close()