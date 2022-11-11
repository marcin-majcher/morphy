import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(0, os.path.join(ROOT_DIR, '..'))

import json
import time
import importlib
import pprint

import click
from chess import (
    Board,
)

from morphy.config import settings
from morphy.cn_utils import Puzzle


def normalize_fen(fen):
    return ' '.join(fen.strip().split())


def save_solution(solution, solutions_file):
    with open(solutions_file, 'a') as f:
        f.write('{}\n'.format(json.dumps(solution)))


def already_solved(solutions_file):
    solved = {}
    try:
        with open(solutions_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    fen = normalize_fen(json.loads(line)['fen'])
                    solved[fen] = line
    except IOError:
        pass
    return solved


def get_solutions_number(p):
    lines = Puzzle.create_lines(p)
    return len(lines)


@click.command()
@click.option('--solutions', '-s', required=True, type=str)
@click.option('--puzzles', '-p', required=True, type=str)
@click.option('--number', '-n', type=int, default=1, show_default=True)
@click.option('--engine', '-e', 'engine_path', required=False, type=str)
@click.option('--settings', '-S', 'settings_module', required=False, type=str)
def main(solutions, puzzles, number, engine_path, settings_module):
    counter = 0
    solved = already_solved(solutions)
    stop_solver = False

    settings_module = settings_module or os.environ.get('MORPHY_SETTINGS_MODULE')

    if settings_module:
        settings.load_settings(importlib.import_module(settings_module))

    engine_path = engine_path or os.environ.get('MORPHY_ENGINE_PATH')

    if engine_path:
        settings['ENGINE_PATH'] = engine_path

    click.echo('-' * 100)
    click.secho('Used settings: \n', fg='green')
    click.echo(pprint.pformat(settings))
    click.echo('-' * 100)
    puzzles_with_solution = [json.loads(p) for p in solved.values()]
    puzzles_with_solution = [p for p in puzzles_with_solution if p['is_solved']]
    click.secho('Solved puzzles: {}'.format(len(puzzles_with_solution)), fg='green')
    click.secho('Unsolved puzzles: {}'.format(len(solved) - len(puzzles_with_solution)), fg='red')
    click.secho('Total: {}'.format(len(solved)), fg='green')
    click.echo('-' * 100)

    assert number >= 1
    assert settings.ENGINE_PATH

    from morphy.solver import Solver
    from morphy.utils import CannotSolve
    from morphy.engine import open_engine
    from morphy.line import Line
    from morphy.constant import (
        MATE_CAT,
    )

    def guess_puzzle_cat(fen, engine):
        solver = Solver(engine, max_line_length=1)
        board = Board(fen)
        line = solver.get_next_comp_line(Line(board))[0]
        return line.get_line_category()

    with open(puzzles, 'r') as puzzles_file:
        for puzzle in puzzles_file:
            fen = normalize_fen(puzzle)

            if fen in solved:
                continue

            if number == counter:
                break

            try:
                engine = open_engine(settings.ENGINE_PATH)

                puzzle_cat = guess_puzzle_cat(fen, engine)

                if puzzle_cat == MATE_CAT:
                    solver = Solver(
                        engine,
                        best_moves_search_conf=settings.BEST_MOVES_SEARCH_MATE_CAT_CONF,
                        max_number_best_moves=settings.MAX_NUMBER_BEST_MOVES_MATE_CAT,
                        max_lines_number=settings.MAX_LINES_NUMBER_MATE_CAT,
                        log_func=click.echo,
                    )
                else:
                    solver = Solver(engine, log_func=click.echo)

                ts = time.time()
                solver.solve(fen)
                save_solution(solver.to_dict(), solutions)
            except CannotSolve:
                save_solution({
                    'fen': normalize_fen(fen),
                    "is_solved": False,
                }, solutions)
            except KeyboardInterrupt:
                click.secho('Stopping solver...', fg='red')
                stop_solver = True
            finally:
                engine.quit()
                if not stop_solver:
                    counter += 1
                    click.secho('Solving time: {}'.format(time.time() - ts), fg='green')

                    is_solved_color = 'green'

                    if not solver.is_solved():
                        is_solved_color = 'red'
                        solutions_number = 0
                    else:
                        solutions_number = get_solutions_number(solver.to_dict())

                    click.secho('Is solved: {}'.format(solver.is_solved()), fg=is_solved_color)

                    if solutions_number:
                        click.secho('Solutions number: {}'.format(solutions_number), fg='green')

                    click.secho('Puzzle number: {}/{}'.format(counter, number), fg='green')
                    click.secho('Puzzle cat: {}'.format(puzzle_cat), fg='green')
                else:
                    break


if __name__ == '__main__':
    main()
