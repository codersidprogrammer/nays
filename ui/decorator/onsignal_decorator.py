from typing import Callable

def OnSignal(signal_name: str):
    def decorator(func: Callable):
        func._bind_to_signal = signal_name
        return func
    return decorator

def bindOnSignal(obj, global_signals):
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if callable(attr) and hasattr(attr, "_bind_to_signal"):
            signal_name = attr._bind_to_signal
            signal = getattr(global_signals, signal_name, None)
            if signal:
                signal.connect(attr)