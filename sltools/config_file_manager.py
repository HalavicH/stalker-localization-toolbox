import configparser
import os


class GeneralConfig:
    def __init__(self, loglevel=None, language=None, show_stacktrace=None):
        self.loglevel = loglevel
        self.language = language
        self.show_stacktrace = show_stacktrace


class FileConfig:
    def __init__(self):
        self.general = GeneralConfig()


class ConfigFileManager:
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser('~'), '.sltools')
        self.config_path = os.path.join(self.config_dir, 'config')
        self.config = configparser.ConfigParser()

        # Ensure the config file exists
        self._ensure_config_exists()

        # Load config into FileConfig object
        self.file_config = FileConfig()
        self.__load_config()

    def _ensure_config_exists(self):
        """Ensure that the config directory and file exist."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        if not os.path.isfile(self.config_path):
            open(self.config_path, 'a').close()

    def __load_config(self):
        """Load the configuration from the file."""
        self.config.read(self.config_path)

        # Update FileConfig object
        self.file_config.general.loglevel = self.config.get('general', 'loglevel', fallback='info')
        self.file_config.general.language = self.config.get('general', 'language', fallback='en')
        self.file_config.general.show_stacktrace = self.config.getboolean('general', 'show_stacktrace', fallback=False)

    def update_config(self, section, key, value):
        """Update a specific configuration setting."""
        self.config.read(self.config_path)

        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value

        # Update the FileConfig object
        if hasattr(self.file_config, section) and hasattr(getattr(self.file_config, section), key):
            setattr(getattr(self.file_config, section), key, value)

        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def get_config(self):
        """Get the FileConfig object."""
        return self.file_config


# File config
file_config = ConfigFileManager().get_config()
