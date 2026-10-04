import sys
from pathlib import Path

from devvault.keys import get


DEVVAULT_DIR = Path.home() / ".devvault"
ENV_FILE = DEVVAULT_DIR / ".env"


def load_keys():
    """Charge toutes les clés depuis le fichier .env."""
    if not ENV_FILE.exists():
        return {}

    keys = {}

    with ENV_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            keys[key.strip()] = value.strip()

    return keys


def set_key(name, value):
    """Ajoute ou modifie une clé."""
    DEVVAULT_DIR.mkdir(parents=True, exist_ok=True)

    keys = load_keys()
    keys[name] = value

    with ENV_FILE.open("w", encoding="utf-8") as file:
        for key, value in keys.items():
            file.write(f"{key}={value}\n")


def delete_key(name):
    """Supprime une clé."""
    keys = load_keys()

    if name not in keys:
        raise KeyError(f"La clé '{name}' n'existe pas.")

    del keys[name]

    DEVVAULT_DIR.mkdir(parents=True, exist_ok=True)

    with ENV_FILE.open("w", encoding="utf-8") as file:
        for key, value in keys.items():
            file.write(f"{key}={value}\n")


def mask_value(value):
    """Masque une valeur sensible."""
    if len(value) <= 4:
        return "*" * len(value)

    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def show_keys():
    """Affiche les clés sans révéler complètement leurs valeurs."""
    keys = load_keys()

    if not keys:
        print("Aucune clé enregistrée.")
        return

    print("Clés enregistrées :")
    print()

    for key, value in keys.items():
        print(f"  {key} = {mask_value(value)}")


def show_help():
    print("DevVault")
    print()
    print("Commandes :")
    print("  set <clé> <valeur>    Ajouter ou modifier une clé")
    print("  get <clé>             Récupérer une clé")
    print("  list                  Afficher les clés")
    print("  keys                  Afficher les clés")
    print("  delete <clé>          Supprimer une clé")
    print("  help                  Afficher cette aide")
    print()
    print(f"Vault : {ENV_FILE}")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "set":
        if len(sys.argv) < 4:
            print("Erreur : arguments manquants.")
            print("Usage : python main.py set <clé> <valeur>")
            sys.exit(1)

        name = sys.argv[2]
        value = sys.argv[3]

        set_key(name, value)
        print(f"OK : clé '{name}' enregistrée.")

    elif command == "get":
        if len(sys.argv) < 3:
            print("Erreur : clé manquante.")
            print("Usage : python main.py get <clé>")
            sys.exit(1)

        try:
            print(get(sys.argv[2]))
        except KeyError as error:
            print(f"Erreur : {error}")
            sys.exit(1)

    elif command in ("list", "keys"):
        show_keys()

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Erreur : clé manquante.")
            print("Usage : python main.py delete <clé>")
            sys.exit(1)

        try:
            delete_key(sys.argv[2])
            print(f"OK : clé '{sys.argv[2]}' supprimée.")
        except KeyError as error:
            print(f"Erreur : {error}")
            sys.exit(1)

    elif command == "help":
        show_help()

    else:
        print(f"Erreur : commande inconnue : {command}")
        print("Utilise 'python main.py help' pour voir les commandes.")
        sys.exit(1)


if __name__ == "__main__":
    main()