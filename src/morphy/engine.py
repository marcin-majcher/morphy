from chess.engine import (
    Limit as _Limit,
    SimpleEngine,
)


class Limit(_Limit):
    
    def __eq__(self, other):
        # TODO: should we better compare floats here?
        return all([
            self.time == other.time,
            self.depth == other.depth,
            self.nodes == other.nodes,
            self.mate == other.mate,
            self.white_clock == other.white_clock,
            self.black_clock == other.black_clock,
            self.white_inc == other.white_inc,
            self.black_inc == other.black_inc,
            self.remaining_moves == other.remaining_moves,
        ])


def open_engine(engine_path=None):
    from morphy.config import settings
    return SimpleEngine.popen_uci(engine_path or settings.ENGINE_PATH)
