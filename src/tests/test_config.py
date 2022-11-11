from morphy.config import settings


def test_load_settings():

    class Settings:
        WINNING_SCORE = 666

    settings.load_settings(Settings)
    assert settings.WINNING_SCORE == Settings.WINNING_SCORE