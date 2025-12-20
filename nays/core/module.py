from abc import ABC
from dataclasses import dataclass, field
from typing import Any, List, Optional, Type, Union

from injector import Injector, inject
from nays.core.route import Route

@dataclass
class Provider:
    """
    Represents a service provider with its abstraction/interface.
    Similar to NestJS provider configuration.
    """
    provide: Type[Any]  # The abstraction/interface
    useClass: Optional[Type[Any]] = None  # Implementation class
    useValue: Optional[Any] = None  # Constant value
    useFactory: Optional[callable] = None  # Factory function
    inject: List[Type[Any]] = field(default_factory=list)  # Dependencies to inject
    
    def __post_init__(self):
        # If useClass is not provided, provide is the implementation
        if self.useClass is None and self.useValue is None and self.useFactory is None:
            self.useClass = self.provide



@dataclass
class ModuleMetadata:
    """
    Module metadata similar to NestJS @Module decorator.
    Contains providers, imports, exports, and routes.
    """
    providers: List[Union[Provider, Type[Any]]] = field(default_factory=list)
    imports: List[Type] = field(default_factory=list)
    exports: List[Union[Provider, Type[Any]]] = field(default_factory=list)
    routes: List['Route'] = field(default_factory=list)


class NaysModuleBase(ABC):
    """
    Base Module class similar to NestJS modules.
    Holds providers, imports, exports, and routes.
    Routes are defined at module level and managed by the module.
    """
    
    providers: List[Union[Provider, Type[Any]]] = []
    imports: List[Type] = []
    exports: List[Union[Provider, Type[Any]]] = []
    routes: List[Route] = []
    
    @classmethod
    def getMetadata(cls) -> ModuleMetadata:
        """Get module metadata"""
        return ModuleMetadata(
            providers=cls.providers,
            imports=cls.imports,
            exports=cls.exports,
            routes=cls.routes
        )
    
    @classmethod
    def register(cls, metadata: ModuleMetadata) -> 'NaysModuleBase':
        """Register module with custom metadata"""
        cls.providers = metadata.providers
        cls.imports = metadata.imports
        cls.exports = metadata.exports
        cls.routes = metadata.routes
        return cls


def NaysModule(
    providers: Optional[List[Union[Provider, Type[Any]]]] = None,
    imports: Optional[List[Type]] = None,
    exports: Optional[List[Union[Provider, Type[Any]]]] = None,
    routes: Optional[List[Route]] = None,
):
    """
    Decorator for NaysModule classes.
    Similar to NestJS @Module decorator.
    
    Usage:
        @NaysModule(
            providers=[MyProvider],
            imports=[OtherModule],
            exports=[MyProvider],
            routes=[MyRoute],
        )
        class MainModule:
            pass
    """
    def decorator(cls):
        # Inherit from NaysModuleBase if not already
        if not issubclass(cls, NaysModuleBase):
            cls = type(cls.__name__, (NaysModuleBase,) + cls.__bases__, dict(cls.__dict__))
        
        # Set module metadata on the class
        cls.providers = providers or []
        cls.imports = imports or []
        cls.exports = exports or []
        cls.routes = routes or []
        
        return cls
    
    return decorator




class ModuleContainer:
    """
    Container that manages modules, their providers, and routes.
    Similar to NestJS ModuleContainer.
    Ensures all providers are ready via injector.
    """
    
    def __init__(self, injector: Injector):
        self.modules: dict[str, NaysModule] = {}
        self.providers: dict[Type[Any], Provider] = {}
        self.routes: dict[str, Route] = {}
        self.injector = injector
        self._initialized = False
    
    def registerModule(self, module: Type[NaysModule], name: str = None):
        """Register a module in the container"""
        module_name = name or module.__name__
        self.modules[module_name] = module
        
        # Register all providers from the module
        metadata = module.getMetadata()
        
        # Register imports first (recursive)
        for imported_module in metadata.imports:
            self.registerModule(imported_module)
        
        # Register providers
        for provider in metadata.providers:
            self._registerProvider(provider, module)
        
        # Register routes
        for route in metadata.routes:
            self._registerRoute(route, module)
    
    def _registerProvider(self, provider: Union[Provider, Type[Any]], module: NaysModule):
        """Register a provider from a module"""
        if isinstance(provider, Provider):
            self.providers[provider.provide] = provider
            self._bindProviderToInjector(provider)
        else:
            # Direct class provider
            provider_obj = Provider(provide=provider, useClass=provider)
            self.providers[provider] = provider_obj
            self._bindProviderToInjector(provider_obj)
    
    def _bindProviderToInjector(self, provider: Provider):
        """Bind provider to injector for dependency injection"""
        if provider.useValue is not None:
            # Bind constant value
            self.injector.binder.bind(provider.provide, to=provider.useValue)
        elif provider.useFactory is not None:
            # Bind factory function - wrap with injector decoration
            if provider.inject:
                # If factory has dependencies, use inject decorator
                @inject
                def factory_with_deps(**kwargs):
                    dependencies = {}
                    for dep in provider.inject:
                        dependencies[dep.__name__.lower() if hasattr(dep, '__name__') else str(dep)] = self.injector.get(dep)
                    return provider.useFactory(**dependencies) if dependencies else provider.useFactory()
                self.injector.binder.bind(provider.provide, to=factory_with_deps)
            else:
                self.injector.binder.bind(provider.provide, to=provider.useFactory)
        elif provider.useClass is not None:
            # Bind class implementation
            self.injector.binder.bind(provider.provide, to=provider.useClass)
        else:
            # Bind provide class to itself
            self.injector.binder.bind(provider.provide, to=provider.provide)
    
    def _createFactoryCallable(self, provider: Provider):
        """Create a callable wrapper for factory providers"""
        @inject
        def factory(**kwargs):
            dependencies = []
            for dep in provider.inject:
                dependencies.append(self.injector.get(dep))
            return provider.useFactory(*dependencies)
        return factory
    
    def _registerRoute(self, route: Route, module: NaysModule):
        """Register a route from a module"""
        if route.path in self.routes:
            raise ValueError(f"Route '{route.path}' already registered")
        self.routes[route.path] = route
    
    def get(self, token: Type[Any]) -> Any:
        """Get an instance of a provider using injector"""
        return self.injector.get(token)
    
    def getAllRoutes(self) -> dict[str, Route]:
        """Get all registered routes"""
        return self.routes
    
    def getRoute(self, path: str) -> Optional[Route]:
        """Get a specific route by path"""
        return self.routes.get(path)
    
    def initialize(self):
        """Initialize all modules and ensure providers are ready"""
        if self._initialized:
            return
        
        # Trigger provider instantiation to ensure they're ready
        for token in self.providers:
            try:
                self.injector.get(token)
            except Exception as e:
                print(f"Warning: Failed to initialize provider {token}: {e}")
        
        self._initialized = True


class ModuleFactory:
    """
    Factory for creating and managing modules.
    Similar to NestJS ApplicationFactory.
    Ensures all providers are registered and ready via injector.
    """
    
    def __init__(self, injector: Injector = None):
        self.injector = injector or Injector()
        self.container = ModuleContainer(self.injector)
        self.modules: List[NaysModule] = []
    
    def register(self, *module_classes: Type[NaysModule]) -> 'ModuleFactory':
        """Register one or more modules"""
        for module_cls in module_classes:
            self.container.registerModule(module_cls)
            self.modules.append(module_cls)
        return self
    
    def get(self, token: Type[Any]) -> Any:
        """Get a provider instance from the container via injector"""
        return self.container.get(token)
    
    def getRoutes(self) -> dict[str, Route]:
        """Get all registered routes from all modules"""
        return self.container.getAllRoutes()
    
    def getRoute(self, path: str) -> Optional[Route]:
        """Get a specific route by path"""
        return self.container.getRoute(path)
    
    def initialize(self):
        """Initialize all modules and ensure all providers are ready"""
        self.container.initialize()
        return self
    
    def onInit(self):
        """Initialize all modules"""
        self.initialize()
        for module in self.modules:
            # Call module initialization if it has onInit
            if hasattr(module, 'onInit'):
                module.onInit()
