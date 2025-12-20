

from typing import Dict, Optional
from injector import Injector

from nays.core.lifecycle import OnDestroy, OnInit
from nays.core.route import Route, RouteType


class Router:
    """
    Router that manages navigation between routes.
    Routes are registered from modules and components are instantiated via injector.
    """
    
    def __init__(self, injector: Injector):
        self.__routes: Dict[str, Route] = {}
        self.__injector: Injector = injector
        self.__currentRoute: Optional[Route] = None
        self.__currentInstance = None
    
    def register(self, route: Route):
        """Register a single route"""
        self.__routes[route.path] = route
    
    def registerRoutes(self, routes: Dict[str, Route]):
        """Register multiple routes from modules"""
        self.__routes.update(routes)
    
    def navigate(self, path: str, data: dict = {}):
        """Navigate to a route"""
        # Close and destroy the previous route
        if self.__currentInstance is not None:
            # Try to hide/close the widget (only for PySide6 views)
            # try:
            #     if hasattr(self.__currentInstance, 'view') and hasattr(self.__currentInstance.view, 'hide'):
            #         # This is a BaseView with a .view attribute
            #         self.__currentInstance.view.hide()
            #     elif hasattr(self.__currentInstance, 'hide'):
            #         # This is a raw PySide6 widget
            #         self.__currentInstance.hide()
            #     elif hasattr(self.__currentInstance, 'close'):
            #         # This is a window/dialog
            #         self.__currentInstance.close()
            # except Exception:
            #     # Silently ignore if we can't close it (e.g., test views)
            #     pass
            
            # Call onDestroy lifecycle hook
            if issubclass(type(self.__currentInstance), OnDestroy) and callable(self.__currentInstance.onDestroy):
                self.__currentInstance.onDestroy()
        
        # Get the route
        route = self.__routes.get(path)
        if not route:
            raise ValueError(f"Route '{path}' not found.")
        
        # Instantiate the route component using the injector
        # The injector will handle dependency injection for the component
        # Pass router explicitly to components that need it (if they have a 'router' parameter)
        constructor_kwargs = {'routeData': data}
        
        # Check if the component's __init__ accepts a 'router' parameter
        import inspect
        sig = inspect.signature(route.component.__init__)
        if 'router' in sig.parameters:
            constructor_kwargs['router'] = self
        
        # Check for other injectable parameters (logger, services, etc.)
        # These will be resolved by the injector automatically
        for param_name, param in sig.parameters.items():
            if param_name not in ('self', 'routeData', 'router'):
                # Try to get this from the injector
                if param.annotation != inspect.Parameter.empty:
                    try:
                        # Attempt to resolve this dependency from the injector
                        resolved = self.__injector.get(param.annotation)
                        constructor_kwargs[param_name] = resolved
                    except Exception:
                        # If not found, let the injector handle it
                        pass
        
        routeInstance = self.__injector.create_object(route.component, constructor_kwargs)
        
        # Set route data if needed
        if hasattr(routeInstance, 'routeParams'):
            routeInstance.routeParams = data
        
        # Call onInit on new route if it implements it
        if (issubclass(type(routeInstance), OnInit) or hasattr(routeInstance, 'onInit')) and callable(getattr(routeInstance, 'onInit', None)):
            routeInstance.onInit()
        
        # Display the route
        widget = routeInstance.view
        self.__currentRoute = route
        self.__currentInstance = routeInstance
        
        if route.routeType == RouteType.DIALOG:
            widget.exec()
        else:
            widget.show()
    
    def back(self):
        """Go back to previous route (if implemented with history)"""
        if self.__currentInstance is not None:
            if hasattr(self.__currentInstance, 'onDestroy') and callable(self.__currentInstance.onDestroy):
                self.__currentInstance.onDestroy()
    
    def getCurrentRoute(self) -> Optional[Route]:
        """Get the current active route"""
        return self.__currentRoute
    
    def logAllRoutes(self, title: str = "Registered Routes"):
        """Log all registered routes from the router"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        if not self.__routes:
            print("No routes registered.")
        else:
            print(f"Total routes: {len(self.__routes)}\n")
            for path, route in sorted(self.__routes.items()):
                route_type = route.routeType.name if hasattr(route.routeType, 'name') else str(route.routeType)
                component_name = route.component.__name__ if hasattr(route.component, '__name__') else str(route.component)
                print(f"  📍 {path:<30} -> {component_name:<25} [{route_type}]")
        
        print(f"{'='*60}\n")
    
    def getRoutes(self) -> Dict[str, Route]:
        """Get all registered routes"""
        return self.__routes.copy()
    
    def getRoutesByType(self, route_type) -> Dict[str, Route]:
        """Get routes filtered by type (e.g., RouteType.DIALOG, RouteType.WINDOW)"""
        return {path: route for path, route in self.__routes.items() if route.routeType == route_type}