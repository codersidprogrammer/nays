import sys
import unittest
from pathlib import Path
from typing import Type

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nays import ModuleMetadata, NaysModule, NaysModuleBase, Provider
from nays.core.route import Route


class TestProvider:
    """Test provider class"""

    pass


class TestService:
    """Test service class"""

    pass


class TestRoute(Route):
    """Test route class"""

    path = "/test"


class TestNaysModuleDecorator(unittest.TestCase):
    """Test cases for NaysModule decorator"""

    def test_decorator_with_no_arguments(self):
        """Test decorator with no arguments"""

        @NaysModule()
        class SimpleModule:
            pass

        # Check if the class inherits from NaysModuleBase
        self.assertTrue(issubclass(SimpleModule, NaysModuleBase))

        # Check if metadata is initialized with empty lists
        self.assertEqual(SimpleModule.providers, [])
        self.assertEqual(SimpleModule.imports, [])
        self.assertEqual(SimpleModule.exports, [])
        self.assertEqual(SimpleModule.routes, [])

    def test_decorator_with_exports(self):
        """Test decorator with exports parameter"""

        @NaysModule(exports=[TestProvider])
        class ExportModule:
            pass

        self.assertTrue(issubclass(ExportModule, NaysModuleBase))
        self.assertEqual(ExportModule.exports, [TestProvider])
        self.assertEqual(ExportModule.providers, [])
        self.assertEqual(ExportModule.imports, [])
        self.assertEqual(ExportModule.routes, [])

    def test_decorator_with_providers(self):
        """Test decorator with providers parameter"""
        provider = Provider(provide=TestService, useClass=TestService)

        @NaysModule(providers=[provider, TestProvider])
        class ProviderModule:
            pass

        self.assertTrue(issubclass(ProviderModule, NaysModuleBase))
        self.assertEqual(len(ProviderModule.providers), 2)
        self.assertIn(provider, ProviderModule.providers)
        self.assertIn(TestProvider, ProviderModule.providers)

    def test_decorator_with_imports(self):
        """Test decorator with imports parameter"""

        @NaysModule()
        class ImportedModule:
            pass

        @NaysModule(imports=[ImportedModule])
        class MainModule:
            pass

        self.assertTrue(issubclass(MainModule, NaysModuleBase))
        self.assertEqual(MainModule.imports, [ImportedModule])

    def test_decorator_with_routes(self):
        """Test decorator with routes parameter"""
        route = TestRoute()

        @NaysModule(routes=[route])
        class RouteModule:
            pass

        self.assertTrue(issubclass(RouteModule, NaysModuleBase))
        self.assertEqual(len(RouteModule.routes), 1)
        self.assertIn(route, RouteModule.routes)

    def test_decorator_with_all_parameters(self):
        """Test decorator with all parameters"""

        @NaysModule()
        class ImportedModule:
            pass

        provider = Provider(provide=TestService, useClass=TestService)
        route = TestRoute()

        @NaysModule(
            providers=[provider, TestProvider],
            imports=[ImportedModule],
            exports=[TestProvider],
            routes=[route],
        )
        class CompleteModule:
            pass

        self.assertTrue(issubclass(CompleteModule, NaysModuleBase))
        self.assertEqual(len(CompleteModule.providers), 2)
        self.assertEqual(CompleteModule.imports, [ImportedModule])
        self.assertEqual(CompleteModule.exports, [TestProvider])
        self.assertEqual(len(CompleteModule.routes), 1)

    def test_get_metadata(self):
        """Test getMetadata method"""

        @NaysModule(exports=[TestProvider])
        class MetadataModule:
            pass

        metadata = MetadataModule.getMetadata()

        self.assertIsInstance(metadata, ModuleMetadata)
        self.assertEqual(metadata.exports, [TestProvider])
        self.assertEqual(metadata.providers, [])
        self.assertEqual(metadata.imports, [])
        self.assertEqual(metadata.routes, [])

    def test_register_method(self):
        """Test register method"""

        @NaysModule()
        class RegisterModule:
            pass

        new_metadata = ModuleMetadata(
            providers=[TestProvider], exports=[TestService], imports=[], routes=[]
        )

        result = RegisterModule.register(new_metadata)

        # Check that the method returns the class
        self.assertEqual(result, RegisterModule)

        # Check that metadata was updated
        self.assertEqual(RegisterModule.providers, [TestProvider])
        self.assertEqual(RegisterModule.exports, [TestService])

    def test_module_inheritance(self):
        """Test that decorated class inherits from NaysModuleBase"""

        @NaysModule()
        class InheritanceModule:
            pass

        # Check MRO (Method Resolution Order)
        self.assertTrue(issubclass(InheritanceModule, NaysModuleBase))

        # Verify methods are available
        self.assertTrue(hasattr(InheritanceModule, "getMetadata"))
        self.assertTrue(hasattr(InheritanceModule, "register"))
        self.assertTrue(callable(InheritanceModule.getMetadata))
        self.assertTrue(callable(InheritanceModule.register))

    def test_multiple_decorated_modules(self):
        """Test that multiple decorated modules have separate metadata"""

        @NaysModule(exports=[TestProvider])
        class ModuleA:
            pass

        @NaysModule(exports=[TestService])
        class ModuleB:
            pass

        # Check that modules have separate metadata
        self.assertEqual(ModuleA.exports, [TestProvider])
        self.assertEqual(ModuleB.exports, [TestService])

        # Check that they are independent
        self.assertNotEqual(ModuleA.exports, ModuleB.exports)

    def test_decorator_preserves_class_name(self):
        """Test that decorator preserves the class name"""

        @NaysModule()
        class NamedModule:
            pass

        self.assertEqual(NamedModule.__name__, "NamedModule")

    def test_decorator_with_existing_methods(self):
        """Test that decorator works with classes that have methods"""

        @NaysModule(exports=[TestProvider])
        class MethodModule:
            def custom_method(self):
                return "custom"

        instance = MethodModule()
        self.assertEqual(instance.custom_method(), "custom")
        self.assertEqual(MethodModule.exports, [TestProvider])

    def test_empty_lists_are_separate_instances(self):
        """Test that each module gets its own list instances"""

        @NaysModule()
        class Module1:
            pass

        @NaysModule()
        class Module2:
            pass

        # Modify Module1's providers
        Module1.providers.append(TestProvider)

        # Module2's providers should remain empty
        self.assertEqual(len(Module1.providers), 1)
        self.assertEqual(len(Module2.providers), 0)


if __name__ == "__main__":
    unittest.main()
