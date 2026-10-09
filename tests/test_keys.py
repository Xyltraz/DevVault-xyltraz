import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from DevVault import keys


class DevVaultKeysTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config_dir = self.root / "config"
        self.vault_dir = self.root / "vault"
        self.config_file = self.config_dir / "config.json"
        self.config_patch = patch.object(keys, "_CONFIG_DIR", self.config_dir)
        self.file_patch = patch.object(keys, "_CONFIG_FILE", self.config_file)
        self.default_patch = patch.object(keys, "_DEFAULT_DIR", self.vault_dir)
        self.config_patch.start()
        self.file_patch.start()
        self.default_patch.start()

    def tearDown(self):
        self.default_patch.stop()
        self.file_patch.stop()
        self.config_patch.stop()
        self.temp.cleanup()

    def test_add_get_round_trip(self):
        keys.add("TEST_KEY", 'hello "world"\nsecond line')
        self.assertEqual(keys.get("TEST_KEY"), 'hello "world"\nsecond line')

    def test_list_does_not_return_values(self):
        keys.add("SECRET", "super-secret")
        self.assertEqual(keys.list_keys(), ["SECRET"])
        self.assertNotIn("super-secret", keys.list_keys())

    def test_remove(self):
        keys.add("TO_REMOVE", "value")
        self.assertTrue(keys.remove("TO_REMOVE"))
        self.assertFalse(keys.remove("TO_REMOVE"))
        self.assertIsNone(keys.get("TO_REMOVE"))

    def test_change_dir_persists(self):
        target = self.root / "other"
        keys.dir(target)
        self.assertEqual(Path(keys.dir()), target.resolve())
        self.assertTrue(self.config_file.exists())

    def test_invalid_key(self):
        with self.assertRaises(ValueError):
            keys.add("BAD KEY", "value")


if __name__ == "__main__":
    unittest.main()
