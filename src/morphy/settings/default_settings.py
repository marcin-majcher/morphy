from morphy.engine import Limit


BEST_MOVE_SEARCH_CONF = {
    'limit': Limit(depth=29),
    'options': {
        'Threads': 4,
        'Hash': 1024,
    }
}

BEST_MOVES_SEARCH_CONF = {
    'limit': Limit(depth=29),
    'multipv': 3,
    'options': {
        'Threads': 8,
        'Hash': 1024,
    }
}

BEST_MOVES_SEARCH_MATE_CAT_CONF = {
    'limit': Limit(depth=20),
    'multipv': 16,
    'options': {
        'Threads': 8,
        'Hash': 1024,
    }
}

WINNING_SCORE = 270
MATE_CLOSE_SCORE = 3
CP_CLOSE_SCORE = 100
MAX_NUMBER_BEST_MOVES = BEST_MOVES_SEARCH_CONF['multipv'] - 1
MAX_NUMBER_BEST_MOVES_MATE_CAT = BEST_MOVES_SEARCH_MATE_CAT_CONF['multipv'] - 1
MAX_LINE_LENGTH = 24
MAX_LINES_NUMBER = 30
MAX_LINES_NUMBER_MATE_CAT = 300
SIMILARITY_FACTOR = 5/3
ENGINE_PATH = ''
