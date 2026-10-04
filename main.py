import sys
from pathlib import Path

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


def get_key(name):
    """Récupère une clé."""
    keys = load_keys()

    if name not in keys:
        raise KeyError(f"La clé '{name}' n'existe pas.")

    return keys[name]


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

    with ENV_FILE.open("w", encoding="utf-8") as file:
        for key, value in keys.items():
            file.write(f"{key}={value}\n")


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
            print("Usage : python main.py set <clé> <valeur>")
            sys.exit(1)

        name = sys.argv[2]
        value = sys.argv[3]

        set_key(name, value)
        print(f"✓ Clé '{name}' enregistrée.")

    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage : python main.py get <clé>")
            sys.exit(1)

        try:
            print(get_key(sys.argv[2]))
        except KeyError as error:
            print(f"✗ {error}")
            sys.exit(1)

    elif command in ("list", "keys"):
        keys = load_keys()

        if not keys:
            print("Aucune clé enregistrée.")
        else:
            print("Clés enregistrées :")

            for key in keys:
                print(f"  - {key}")

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage : python main.py delete <clé>")
            sys.exit(1)

        try:
            delete_key(sys.argv[2])
            print(f"✓ Clé '{sys.argv[2]}' supprimée.")
        except KeyError as error:
            print(f"✗ {error}")
            sys.exit(1)

    elif command == "help":
        show_help()

    else:
        print(f"✗ Commande inconnue : {command}")
        print("Utilise 'python main.py help' pour voir les commandes.")
        sys.exit(1)


if __name__ == "__main__":
    main()