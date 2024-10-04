from dynaconf import Dynaconf

def get_settings():
    settings = Dynaconf(settings_files=["settings.yaml"], environments=True)
    return settings

settings = get_settings()
