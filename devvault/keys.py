from pathlib import Path


DEVVAULT_DIR = Path.home() / ".devvault"
ENV_FILE = DEVVAULT_DIR / ".env"


def _load_keys():
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


class Keys:
    def __getattr__(self, name):
        keys = _load_keys()

        if name not in keys:
            raise AttributeError(
                f"La clé '{name}' n'existe pas dans DevVault."
            )

        return keys[name]


keys = Keys()


def get(name):
    """Récupère une clé par son nom."""
    values = _load_keys()

    if name not in values:
        raise KeyError(f"La clé '{name}' n'existe pas dans DevVault.")

    return values[name]