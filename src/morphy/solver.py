import copy

from chess import (
    Board,
)

from morphy.line import Line
from morphy.utils import (
    extract_best_winning_moves,
    close_score_threshold,
    score,
    cannot_solve,
    flatten,
)
from morphy.constant import MATERIAL_CAT
from morphy.config import settings


class Solver:
    
    def __init__(self, engine, best_move_search_conf=settings.BEST_MOVE_SEARCH_CONF,
                 best_moves_search_conf=settings.BEST_MOVES_SEARCH_CONF, max_number_best_moves=settings.MAX_NUMBER_BEST_MOVES,
                 max_line_length=settings.MAX_LINE_LENGTH, max_lines_number=settings.MAX_LINES_NUMBER,
                 cp_close_score=settings.CP_CLOSE_SCORE, mate_close_score=settings.MATE_CLOSE_SCORE,
                 similarity_factor=settings.SIMILARITY_FACTOR, log_func=None):
        self._closed_lines = []
        self._open_lines = []
        self._fen = None
        self._depth = 0
        self.engine = engine
        self.best_move_search_conf = copy.deepcopy(best_move_search_conf)
        self.best_moves_search_conf = copy.deepcopy(best_moves_search_conf)
        self.max_number_best_moves = max_number_best_moves
        self.max_line_length = max_line_length
        self.max_lines_number = max_lines_number
        self.log_func = log_func
        self.cp_close_score = cp_close_score
        self.mate_close_score = mate_close_score
        self.similarity_factor = similarity_factor

    def reset(self):
        self._closed_lines = []
        self._open_lines = []
        self._fen = None
        self._depth = 0
           
    def solve(self, fen):
        self.log('-' * 100)
        self.log('{}'.format(fen))
        self.log('\n')
        self.print_board(fen)
        self.log('\n')
        self._fen = fen
        board = Board(fen)
        assert not board.is_game_over()
        self._open_lines.append(Line(board))

        while self._open_lines:
            # Calculate new lines
            lines = self._go_deeper()
            # Evaluate lines
            self._evaluate_lines(flatten(lines))
            # Should solver stop searching
            self.should_terminate(lines)
            # Remove already checked lines
            lines = self.remove_repetitions(flatten(lines))
            self._move_to_closed_lines(lines)
            self._replace_open_lines(lines)
            self.log('Open lines: {}'.format(len(self._open_lines)))
            self.log('Closed lines: {}'.format(len(self._closed_lines)))
    
    def remove_repetitions(self, lines):
        return [l for l in lines if not l.has_repetition()]

    def _evaluate_lines(self, lines):
        for l in lines:
            l.evaluate()
    
    def stop_if_broken_line(self, lines):
        if [] in lines:
            self.log('Broken line!')
            cannot_solve()
    
    def stop_if_solution_too_long(self, lines):
        for l in flatten(lines):
            if l.length() > self.max_line_length:
                self.log('Solution too long: {}!'.format(l.length))
                cannot_solve()
    
    def stop_if_too_many_solutions(self):
        solutions_number = len(self._open_lines) + len(self._closed_lines)
        if solutions_number > self.max_lines_number:
            self.log('Too many solutions: {}!'.format(solutions_number))
            cannot_solve()
    
    def stop_if_too_many_good_moves(self, lines):
        for l in lines:
            if len(l) > self.max_number_best_moves:
                self.log('Too many good moves: {}!'.format(len(l)))
                cannot_solve()

    def filter_winning_material_solutions(self, lines):
        _lines = []
        
        for i in lines:
            if not all([j.is_closed() and (j.get_line_category() == MATERIAL_CAT) for j in i]):
                _lines.append(i)
        
        return _lines

    def should_terminate(self, lines):
        # Broken line
        self.stop_if_broken_line(lines)
        
        # Too many good moves
        self.stop_if_too_many_good_moves(self.filter_winning_material_solutions(lines))
        
        # Solution too long
        self.stop_if_solution_too_long(lines)

        # Too many solutions
        self.stop_if_too_many_solutions()
    
    def _go_deeper(self):
        lines = []
        for line in self._open_lines:
            if line.is_player_move():
                next_lines = self.get_next_player_lines(line)
            else:
                next_lines = self.get_next_comp_line(line)

            lines.append(next_lines)
            # Does this make solver faster?
            # Evaluate lines
            self._evaluate_lines(flatten(lines))
            # Should solver stop searching
            self.should_terminate(lines)

        self._depth += 1
        return lines
            
    def _move_to_closed_lines(self, lines):
        for l in lines:
            if l.is_closed():
                self._closed_lines.append(l)

    def _replace_open_lines(self, lines):
        self._open_lines = [l for l in lines if l.is_open()]
    
    def analyse(self, line, **kwargs):
        return self.engine.analyse(line.board, **kwargs)

    def calc_cp_threshold(self, infos, line):
        scores = [score(i) for i in infos]
        scores.sort(reverse=True)
        return (self.cp_close_score if scores[0].is_mate() else
                close_score_threshold(scores[0], similarity_factor=self.similarity_factor))

    def calc_mate_threshold(self, line):
        mt = self.mate_close_score - (line.length() // 2)
        return mt if mt > 0 else 0

    def extract_best_winning_moves(self, infos, line):
        cp_threshold = self.calc_cp_threshold(infos, line)
        mate_threshold = self.calc_mate_threshold(line)
        best_scores = extract_best_winning_moves(
            [score(i) for i in infos],
            cp_threshold=cp_threshold,
            mate_threshold=mate_threshold,
        )
        return [i for i in infos if score(i) in best_scores and i.get('pv')]
    
    def get_next_player_lines(self, line):
        infos = list(self.search_best_moves(line))
        best_moves = self.extract_best_winning_moves(infos, line)
        
        return [line.make_move(i['pv'][0], i) for i in best_moves]

    def get_next_comp_line(self, line):
        info = self.search_best_move(line)
        return [line.make_move(info['pv'][0], info)]

    def search_best_move(self, line, **kwargs):
        kw = copy.deepcopy(self.best_move_search_conf)
        kw.update(kwargs)
        assert 'multipv' not in kw
        return self.analyse(line, **kw)
    
    def search_best_moves(self, line, **kwargs):
        kw = copy.deepcopy(self.best_moves_search_conf)
        kw.update(kwargs)
        assert kw.get('multipv', 0) > 1
        return self.analyse(line, **kw)
    
    def log(self, msg, *args, **kwargs):
        if self.log_func:
            self.log_func(msg, *args, **kwargs)

    def is_solved(self):
        return not self._open_lines

    def to_dict(self):
        return {
            'is_solved': self.is_solved(),
            'lines': [l.to_dict() for l in self._closed_lines],
            'fen': self._fen,
        }

    def print_board(self, fen):
        self.log(Board(fen))