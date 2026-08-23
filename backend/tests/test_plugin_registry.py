import unittest

from app.plugins import registry
from app.plugins.fcc_plugin import FccPlugin


class PluginRegistryTests(unittest.TestCase):
    def setUp(self):
        registry._REGISTRY.clear()

    def test_loads_plugin_by_agency_code(self):
        plugin = registry.get_plugin("FCC")
        self.assertIsInstance(plugin, FccPlugin)

    def test_raises_for_unknown_agency(self):
        with self.assertRaises(ValueError):
            registry.get_plugin("unknown")


if __name__ == "__main__":
    unittest.main()
