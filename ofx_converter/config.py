from dynaconf import Dynaconf

def get_settings():
    settings = Dynaconf(use_dotenv=True, environments=True)
    return settings["converter"]

settings = get_settings()
