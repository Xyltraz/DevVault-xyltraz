"""Command-line interface for DevVault."""

from __future__ import annotations

import sys
from DevVault import keys

HELP = """DevVault — coffre local de clés et de valeurs

Commandes :
  devvault add NOM VALEUR       Ajoute une clé ou remplace sa valeur
  devvault list                 Liste les noms, sans afficher les valeurs
  devvault show NOM             Affiche la valeur d'une clé
  devvault remove NOM           Supprime une clé
  devvault --change-dir PATH    Change le dossier contenant .env
  devvault help                 Affiche cette aide
  devvault ?                    Affiche cette aide

Exemples :
  devvault add DISCORD_TOKEN "ma valeur secrète"
  devvault list
  devvault show DISCORD_TOKEN
  devvault remove DISCORD_TOKEN
  devvault --change-dir "F:\\dev\\secrets"

API Python :
  from DevVault import keys
  keys.dir()                       # dossier actuel, sans .env
  keys.dir(r"F:\\dev\\secrets")    # change le dossier et le mémorise
  keys.get("DISCORD_TOKEN")        # valeur, ou None si absente
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0].lower() in {"help", "?"}:
        print(HELP)
        return 0

    try:
        if args[0] == "--change-dir":
            if len(args) != 2:
                print("Erreur : utilise devvault --change-dir PATH", file=sys.stderr)
                return 2
            print(f"Dossier DevVault : {keys.dir(args[1])}")
            return 0

        command = args[0].lower()
        if command == "add":
            if len(args) < 3:
                print("Erreur : utilise devvault add NOM VALEUR", file=sys.stderr)
                return 2
            name = args[1]
            value = " ".join(args[2:])
            keys.add(name, value)
            print(f"Clé '{name}' enregistrée.")
            return 0

        if command == "list":
            if len(args) != 1:
                print("Erreur : utilise devvault list", file=sys.stderr)
                return 2
            names = keys.list_keys()
            if not names:
                print("Aucune clé enregistrée.")
            else:
                for name in names:
                    print(name)
            return 0

        if command == "show":
            if len(args) != 2:
                print("Erreur : utilise devvault show NOM", file=sys.stderr)
                return 2
            value = keys.get(args[1])
            if value is None:
                print(f"Clé '{args[1]}' introuvable.", file=sys.stderr)
                return 1
            print(value)
            return 0

        if command == "remove":
            if len(args) != 2:
                print("Erreur : utilise devvault remove NOM", file=sys.stderr)
                return 2
            if keys.remove(args[1]):
                print(f"Clé '{args[1]}' supprimée.")
                return 0
            print(f"Clé '{args[1]}' introuvable.", file=sys.stderr)
            return 1

        print(f"Commande inconnue : {args[0]}\n")
        print(HELP)
        return 2

    except (ValueError, OSError) as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
