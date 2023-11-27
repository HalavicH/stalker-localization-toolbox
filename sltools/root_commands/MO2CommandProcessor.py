from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn


class MO2CommandProcessor(AbstractCommand):
    # Not relevant to command processor
    def _process_file(self, file_path, results: dict, args):
        pass

    def display_result(self, result: dict):
        pass

    def __init__(self, commands: list):
        self.commands = commands
        self._registry = {}

        for cmd in self.commands:
            self._registry[cmd.get_name()] = cmd
            for alias in cmd.get_aliases():
                self._registry[alias] = cmd

    # Metadata
    ##########
    def get_name(self) -> str:
        return "mo2"

    def get_aliases(self) -> list:
        return []

    def _get_help(self) -> str:
        return trn('Commands for managing and processing Mod Organizer 2 (MO2) mods')

    def _setup_parser_args(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', help=trn('Sub-commands available:'))

        for cmd in self.commands:
            log.debug("Processing: " + cmd.get_name())
            cmd.setup(subparsers)

    def execute(self, args) -> {}:
        command_name = args.subcommand
        command = self._registry.get(command_name)

        if command:
            log.debug(f"Executing command: {command_name}")
            result = command.execute(args)
            command.display_result(result)
            return result
        else:
            log.error(f"Command not found: {command_name}")
            return {}
