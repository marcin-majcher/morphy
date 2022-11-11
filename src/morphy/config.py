import inspect

from morphy.settings import default_settings


class Settings(dict):

    def load_settings(self, settings):
        _settings = [
            s
            for s in inspect.getmembers(settings, lambda x: not inspect.isbuiltin(x))
            if s[0].isupper()
        ]

        for s, v in _settings:
            self[s] = v

    def __getattr__(self, item):
        if item in self:
            return self[item]

        raise AttributeError


settings = Settings()
settings.load_settings(default_settings)