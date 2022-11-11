from chess import (
    KNIGHT,
    ROOK,
    WHITE,
)

from morphy.utils import (
    black_material,
    white_material,
    score,
    cannot_solve,
)
from morphy.constant import (
    PIECE_VALUES,
    UNKNOWN_CAT,
    MATE_CAT,
    MATERIAL_CAT,
)


class Line:
    
    def __init__(self, board):
        self.board = board
        self._closed = False
        self._player_color = self.get_player_color()
        self._analysis_result = []
        self._initial_player_material = self.get_player_material()
        self._initial_comp_material = self.get_comp_material()
        self._parent = None
        self._children = []
        self._repeated_position = False
        
    def get_player_color(self):
        return self.board.root().turn
    
    def copy(self):
        new_line = type(self)(self.board.copy())
        new_line._closed = self._closed
        new_line._analysis_result = self._analysis_result[:]
        new_line._initial_comp_material = self._initial_comp_material
        new_line._initial_player_material = self._initial_player_material
        new_line._parent = self
        new_line._repeated_position = self._repeated_position
        self._children.append(new_line)
        return new_line
    
    def _make_move(self, move):
        self.board.push(move)
    
    def make_move(self, move, info=None):
        assert not self.is_closed()
        line = self.copy()
        line._make_move(move)
        line._analysis_result.append(info)
        return line
    
    def close(self):
        self._closed = True
    
    def is_closed(self):
        return self._closed
    
    def is_open(self):
        return not self.is_closed()
    
    def is_player_move(self):
        return self.board.turn == self._player_color
    
    def get_player_material(self):
        if self._player_color is WHITE:
            return white_material(self.board)
        return black_material(self.board)
    
    def get_comp_material(self):
        if self._player_color is WHITE:
            return black_material(self.board)
        return white_material(self.board)

    def player_won_game(self):
        return self.board.is_checkmate() and not  self.is_player_move()

    def player_gained_material(self):
        return (
            ((self.get_player_material() - self.get_comp_material()) - 
            (self._initial_player_material - self._initial_comp_material)) 
            >= (PIECE_VALUES[ROOK] - PIECE_VALUES[KNIGHT])
        )
    
    def can_close_material_line(self):
        # We always close material line on player move (P (gained material) - C - P (close))
        return (
            self.get_line_category() == MATERIAL_CAT and
            self._parent is not None and
            self._parent.player_gained_material() and
            len(self._parent._children) > 1 and
            self.length() > 3
        )
    
    def get_line_category(self):
        if not self._analysis_result or not self._analysis_result[-1]:
            return UNKNOWN_CAT
        
        if score(self._analysis_result[-1]).is_mate():
            return MATE_CAT
        
        return MATERIAL_CAT
    
    def evaluate(self):
        self._repeated_position = self.is_repetition()
        
        if self.player_won_game() or self.can_close_material_line():
            self.close()
            return 
        
        if self.board.is_game_over(claim_draw=True):
            cannot_solve()
    
    def moves(self):
        return self.board.move_stack
    
    def length(self):
        return len(self.board.move_stack)
    
    def is_repetition(self):
        return self.board.is_repetition(2)

    def has_repetition(self):
        return self._repeated_position

    def to_dict(self):
        return {
            'category': self.get_line_category(),
            'is_closed': self.is_closed(),
            'player_color': self.get_player_color(),
            'moves': [m.uci() for m in self.board.move_stack],
            'initial_player_material': self._initial_player_material,
            'initial_comp_material': self._initial_comp_material,
            'player_material': self.get_player_material(),
            'comp_material': self.get_comp_material(),
        }