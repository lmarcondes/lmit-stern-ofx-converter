from functools import lru_cache

from dynaconf import Dynaconf, LazySettings


@lru_cache
def get_settings() -> LazySettings:
    settings = Dynaconf(use_dotenv=True, environments=True)
    return settings["converter"]

settings = get_settings()
