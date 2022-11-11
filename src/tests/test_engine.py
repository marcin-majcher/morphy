from unittest import mock

from morphy.engine import open_engine
from morphy.settings.default_settings import ENGINE_PATH


@mock.patch('morphy.engine.SimpleEngine')
def test_open_engine(mocked_SimpleEngine):
    e = open_engine()
    mocked_SimpleEngine.popen_uci.assert_called_with(ENGINE_PATH)
    assert e == mocked_SimpleEngine.popen_uci.return_value
    ep = 'path_to_stockfish'
    e = open_engine(ep)
    mocked_SimpleEngine.popen_uci.assert_called_with(ep)
    assert e == mocked_SimpleEngine.popen_uci.return_value
