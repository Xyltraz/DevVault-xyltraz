import subprocess
import sys
from pathlib import Path


def run_command(*args):
    """Exécute main.py et retourne le résultat."""
    return subprocess.run(
        [sys.executable, "main.py", *args],
        capture_output=True,
        text=True
    )


def show_result(result):
    """Affiche les sorties utiles en cas d'échec."""
    print(f"  Code retour : {result.returncode}")
    print(f"  stdout      : {result.stdout!r}")
    print(f"  stderr      : {result.stderr!r}")


def test_help():
    result = run_command("help")

    assert result.returncode == 0
    assert "DevVault" in result.stdout
    assert "set" in result.stdout
    assert "get" in result.stdout
    assert "delete" in result.stdout


def test_missing_command():
    result = run_command()

    assert result.returncode == 0
    assert "DevVault" in result.stdout


def test_unknown_command():
    result = run_command("THIS_COMMAND_DOES_NOT_EXIST")

    assert result.returncode != 0
    assert "Erreur : commande inconnue" in result.stdout


def test_missing_key():
    result = run_command(
        "get",
        "DEVVAULT_TEST_KEY_THAT_DOES_NOT_EXIST_123456"
    )

    assert result.returncode != 0
    assert "n'existe pas" in result.stdout


def test_missing_set_arguments():
    result = run_command("set", "TEST")

    assert result.returncode != 0
    assert "Usage" in result.stdout


def test_missing_get_arguments():
    result = run_command("get")

    assert result.returncode != 0
    assert "Usage" in result.stdout


def test_missing_delete_arguments():
    result = run_command("delete")

    assert result.returncode != 0
    assert "Usage" in result.stdout


def test_python_api():
    from devvault import get, keys

    assert callable(get)
    assert hasattr(keys, "__getattr__")


def test_masking():
    from main import mask_value

    assert mask_value("bonjour") == "bo***ur"
    assert mask_value("abcd") == "****"
    assert mask_value("abc") == "***"


def test_project_structure():
    required_files = [
        Path("main.py"),
        Path("README.md"),
        Path(".gitignore"),
        Path("pyproject.toml"),
        Path("devvault/__init__.py"),
        Path("devvault/keys.py"),
    ]

    for file in required_files:
        assert file.exists(), f"Fichier manquant : {file}"


def main():
    tests = [
        test_help,
        test_missing_command,
        test_unknown_command,
        test_missing_key,
        test_missing_set_arguments,
        test_missing_get_arguments,
        test_missing_delete_arguments,
        test_python_api,
        test_masking,
        test_project_structure,
    ]

    passed = 0

    print("DevVault - Tests")
    print("=" * 30)
    print()

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1

        except AssertionError as error:
            print(f"✗ {test.__name__}")

            if error:
                print(f"  {error}")

            result = run_command(
                "THIS_COMMAND_DOES_NOT_EXIST"
                if test.__name__ == "test_unknown_command"
                else "get",
                *(
                    ["DEVVAULT_TEST_KEY_THAT_DOES_NOT_EXIST_123456"]
                    if test.__name__ == "test_missing_key"
                    else []
                )
            )

            show_result(result)

        except Exception as error:
            print(f"✗ {test.__name__}")
            print(f"  Erreur : {error}")

    print()
    print("=" * 30)
    print(f"Résultat : {passed}/{len(tests)} tests réussis")

    if passed == len(tests):
        print("✓ DevVault est OK.")
        sys.exit(0)

    print("✗ Des tests ont échoué.")
    sys.exit(1)


if __name__ == "__main__":
    main()