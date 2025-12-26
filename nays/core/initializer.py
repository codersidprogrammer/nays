from dataclasses import dataclass
import os
import yaml

@dataclass
class YamlConfigModel:
    name: str
    description: str
    type: str
    defaultValueIndex: int
    items: list

class YamlConfigLoader:
    """
    A class to load YAML configuration files.
    This class is designed to be used as a singleton.
    """
    
    def __init__(self, config_path="config.yml"):
        self.config_path = config_path
        self._data = None
        self._currentData: dict | list = None
        # self.load_yaml()
        
    def setConfigPath(self, config_path: str):
        self.config_path = config_path
        self.load_yaml()

    def load_yaml(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, self.config_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"YAML config file not found: {full_path}")

        with open(full_path, "r") as file:
            self._data = yaml.safe_load(file)
            
    def getGroup(self, group: str):
        """Return the whole group dictionary/list."""
        self._currentData = self._data.get(group, None)
        return self
    
    def getSubgroup(self, subgroup: str):
        """Return the subgroup (list or dict) inside a group."""
        if self._currentData is None:
            return None
        self._currentData = self._currentData.get(subgroup, None)
        return self
    
    def filter(self, key: str, value: any):
        """
        Filter the current data by a key-value pair.
        Returns a new instance with the filtered data.
        """
        if self._currentData is None:
            return None
        if isinstance(self._currentData, list):
            self._currentData = [item for item in self._currentData if item.get(key) == value]
        elif isinstance(self._currentData, dict):
            self._currentData = {k: v for k, v in self._currentData.items() if v.get(key) == value}
        return self
    
    def get(self, isFirst: bool = None) -> dict | list:
        if isFirst is not None:
            if isinstance(self._currentData, list):
                if isFirst and self._currentData:
                    return self._currentData[0]
                elif not isFirst and len(self._currentData) > 1:
                    return self._currentData[1:]
            return self._currentData
        return self._currentData    
    

class YamlInitializer:
    _instance = None  # Singleton instance

    def __new__(cls, config_path="config.yml"):
        if cls._instance is None:
            cls._instance = super(YamlInitializer, cls).__new__(cls)
            cls._instance._load_yaml(config_path)
        return cls._instance

    def _load_yaml(self, config_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, config_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"YAML config file not found: {full_path}")

        with open(full_path, "r") as file:
            self._data = yaml.safe_load(file)

    def get_group(self, group: str):
        """Return the whole group dictionary/list."""
        return self._data.get(group, None)

    def get_subgroup(self, group: str, subgroup: str):
        """Return the subgroup (list or dict) inside a group."""
        group_data = self._data.get(group, None)
        if group_data is None:
            return None
        return group_data.get(subgroup, None)

    def get_items(self, group: str, subgroup: str = None, name: str = None):
        """
        Get items from a group, optionally a subgroup, and optionally by name.
        If subgroup is None, look for 'component' in group.
        If name is provided, filter by name.
        """
        if subgroup:
            data = self.get_subgroup(group, subgroup)
        else:
            data = self.get_subgroup(group, 'component')
        if data is None:
            return []
        if name:
            for entry in data:
                if entry.get('name') == name:
                    return entry.get('items', [])
            return []
        # If no name, return all items in all entries
        items = []
        for entry in data:
            items.extend(entry.get('items', []))
        return items

    def get_value(self, group: str, subgroup: str, name: str):
        """
        Get the value (dict) for a specific name in a subgroup of a group.
        """
        data = self.get_subgroup(group, subgroup)
        if data is None:
            return None
        for entry in data:
            if entry.get('name') == name:
                return entry
        return None

    def setByGroupAndSub(self, group: str, sub: str, value: any):
        if group not in self._data:
            self._data[group] = {}
        self._data[group][sub] = value
