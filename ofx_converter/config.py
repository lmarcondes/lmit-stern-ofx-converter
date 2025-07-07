from dynaconf import Dynaconf, LazySettings


def get_settings() -> LazySettings:
    settings = Dynaconf(use_dotenv=True, environments=True)
    return settings["converter"]

settings = get_settings()
