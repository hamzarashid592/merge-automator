import json
from threading import Lock

class ConfigurationManager:
    _instance = None
    _lock = Lock()  # For thread safety

    def __new__(cls, config_file="config.json"):
        """
        Singleton instance creation.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigurationManager, cls).__new__(cls)
                cls._instance._config_file = config_file
                cls._instance._config_data = cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """
        Load configuration from the JSON file.
        """
        try:
            with open(self._config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Configuration file {self._config_file} not found.")
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON configuration: {str(e)}")

    def get(self, key, default=None):
        """
        Get a configuration value.
        """
        return self._config_data.get(key, default)

    def set(self, key, value):
        """
        Update a configuration value.
        """
        self._config_data[key] = value
        self._save_config()

    def reload(self):
        """
        Reload the configuration from the file.
        """
        self._config_data = self._load_config()

    def _save_config(self):
        """
        Save the updated configuration back to the file.
        """
        with open(self._config_file, "w") as file:
            json.dump(self._config_data, file, indent=4)
