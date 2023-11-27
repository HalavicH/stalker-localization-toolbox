from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.baseline.parser_definitions import BooleanAction
from sltools.config_file_manager import ConfigFileManager
from sltools.utils.colorize import cf_cyan
from sltools.utils.lang_utils import trn


class Config(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "config"

    def get_aliases(self) -> list:
        return ['cfg']

    def _get_help(self) -> str:
        return trn('Configure application settings')

    def _setup_parser_args(self, parser):
        parser.add_argument('--loglevel', help=trn('Set default log level. (Available: %s)') % ["debug", "info", "warning", "error"])
        parser.add_argument('--language', help=trn('Set app language. (Available: %s)') % ["en", "uk"])
        parser.add_argument('--show-stacktrace', action=BooleanAction, type=str, default=None,
                            help=trn('Enable/Disable showing error stack trace (Available: True/False)'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        pass

    def execute(self, args) -> dict:
        """Handle the config command to update the settings."""
        config_manager = ConfigFileManager()

        console = get_console()
        if args.loglevel is not None:
            config_manager.update_config('general', 'loglevel', args.loglevel)
            console.print(cf_cyan(trn("Set new default log level to '%s'") % args.loglevel))

        if args.language is not None:
            config_manager.update_config('general', 'language', args.language)
            console.print(cf_cyan(trn("Set new app language to '%s'") % args.language))

        if args.show_stacktrace is not None:
            show_stacktrace_value = 'yes' if args.show_stacktrace else 'no'
            config_manager.update_config('general', 'show_stacktrace', show_stacktrace_value)
            if args.show_stacktrace:
                console.print(cf_cyan(trn("Stacktrace printing on failure ENABLED")))
            else:
                console.print(cf_cyan(trn("Stacktrace printing on failure DISABLED")))

        return {}

    # Displaying
    ############
    def display_result(self, result: dict):
        pass
