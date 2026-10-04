from pathlib import Path


DEVVAULT_DIR = Path.home() / ".devvault"
ENV_FILE = DEVVAULT_DIR / ".env"


def _load_keys():
    """Charge les clés depuis le coffre DevVault."""
    if not ENV_FILE.exists():
        return {}

    result = {}

    with ENV_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()

    return result


def get(name):
    """Récupère une clé DevVault."""
    keys = _load_keys()

    if name not in keys:
        raise KeyError(f"La clé '{name}' n'existe pas dans DevVault.")

    return keys[name]


class Keys:
    """Permet d'accéder aux clés avec keys.NOM_DE_LA_CLE."""

    def __getattr__(self, name):
        try:
            return get(name)
        except KeyError as error:
            raise AttributeError(str(error)) from error


keys = Keys()