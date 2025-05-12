import json
import os

class ConfigurationManager:
    def __init__(self, config_file="config.json", common_file="configs/common.json"):
        self._config_file = config_file
        self._common_file = common_file
        self._config_data = self._load_config()

    def _load_config(self):
        config_data = {}
        try:
            if os.path.exists(self._common_file):
                with open(self._common_file, "r") as file:
                    config_data.update(json.load(file))
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding common config JSON: {str(e)}")

        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, "r") as file:
                    config_data.update(json.load(file))
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding project config JSON: {str(e)}")

        if not config_data:
            raise Exception(f"No valid configuration found in {self._common_file} or {self._config_file}.")

        return config_data

    def get(self, key, default=None):
        return self._config_data.get(key, default)

    def set(self, key, value):
        # Load ONLY the project-level config as dict
        project_config = self.get_project_only()

        # Update the specific key
        project_config[key] = value

        # Save only updated project config
        with open(self._config_file, "w") as f:
            json.dump(project_config, f, indent=4)


    def reload(self):
        self._config_data = self._load_config()


    def to_dict(self):
        return self._config_data
    
    def get_sources(self):
        """
        Return two dicts: one from common config, one from project-specific config.
        """
        common_config = {}
        project_config = {}

        if os.path.exists(self._common_file):
            with open(self._common_file, "r") as file:
                common_config = json.load(file)

        if os.path.exists(self._config_file):
            with open(self._config_file, "r") as file:
                project_config = json.load(file)

        return common_config, project_config

    def get_project_only(self):
        """
        Return only the keys that are declared in the project-specific config file.
        """
        if os.path.exists(self._config_file):
            with open(self._config_file, "r") as f:
                return json.load(f)
        return {}
