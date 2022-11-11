from morphy.engine import Limit
BEST_MOVE_SEARCH_CONF = {
    'limit': Limit(depth=13),
    'options': {
        'Threads': 4,
        'LogFile': '/home/mortadel/Tmp/lc0.txt',
        'WeightsFile': '/home/mortadel/Pobrane/weights_run1_610313.pb.gz',
        'Use NNUE': True,
        #'Backend': 'cudnn',
    }
}

BEST_MOVES_SEARCH_CONF = {
    'limit': Limit(depth=13),
    'multipv': 3,
    'options': {
        'Threads': 8,
        'LogFile': '/home/mortadel/Tmp/lc0.txt',
        'WeightsFile': '/home/mortadel/Pobrane/weights_run1_610313.pb.gz',
        'Use NNUE': True,
        #'Backend': 'cudnn',
    }
}

BEST_MOVES_SEARCH_MATE_CAT_CONF = {
    'limit': Limit(depth=13),
    'multipv': 16,
    'options': {
        'Threads': 8,
        'LogFile': '/home/mortadel/Tmp/lc0.txt',
        'WeightsFile': '/home/mortadel/Pobrane/weights_run1_610313.pb.gz',
        'Use NNUE': True,
        #'Backend': 'cudnn',
    }
}

ENGINE_PATH = '/home/mortadel/Projects/lc0/build/release/lc0'
