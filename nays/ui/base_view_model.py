import inspect
import logging

from PySide6.QtCore import QObject, Signal,SignalInstance
from typing import Callable, Dict, List, Optional

from colorama import Fore, Style

from nays.core.logger import setupLogger


class BaseViewModel(QObject):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._bindings: Dict[SignalInstance, List[Callable]] = {}
        self._auto_bind_methods()
        self.logger = setupLogger(self.__class__.__name__)
    
    def bind(self, signal: SignalInstance, callback: Callable):
        try:
            signal.connect(callback)
            self._bindings.setdefault(signal, []).append(callback)
            self.logger.debug(f"Bound {callback} to {signal}")
        except Exception as e:
            self.logger.warning(f"Failed to bind {callback} to {signal}: {e}")
            
    def unbind(self, signal: SignalInstance, callback: Optional[Callable] = None):
        if signal in self._bindings:
            callbacks = self._bindings[signal]
            if callback:
                try:
                    signal.disconnect(callback)
                    callbacks.remove(callback)
                except Exception as e:
                    self.logger.warning(f"Failed to unbind {callback} from {signal}: {e}")
            else:
                for cb in callbacks:
                    try:
                        signal.disconnect(cb)
                    except Exception as e:
                        self.logger.warning(f"Failed to unbind {cb} from {signal}: {e}")
                self._bindings[signal] = []
                
    def unbind_all(self):
        for signal, callbacks in self._bindings.items():
            for cb in callbacks:
                try:
                    signal.disconnect(cb)
                except Exception as e:
                    self.logger.warning(f"Failed to unbind {cb} from {signal}: {e}")
        self._bindings.clear()
        
    def get_signals(self) -> Dict[str, Signal]:
        return {
            name: attr for name, attr in inspect.getmembers(self.__class__)
            if isinstance(attr, Signal)
        }

    def _auto_bind_methods(self):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            signal_name = getattr(method, "_bind_to_signal", None)
            if signal_name:
                signal = getattr(self, signal_name, None)
                if isinstance(signal, Signal):
                    self.bind(signal, method)