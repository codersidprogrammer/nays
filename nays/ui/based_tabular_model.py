from dataclasses import dataclass, field


@dataclass
class BasedTabularDataModel:
    name: str = ""
    description: str = ""
    type: str = ""
    defaultValueIndex: int | float = 0
    items: list[any] = field(default_factory=lambda: [])


@dataclass
class TableHandlerDataModel:
    id: int | str = None
    name: str = ""
    description: str = ""
    type: str = ""
    defaultValueIndex: int | float = 0
    items: list[any] = field(default_factory=lambda: [])
