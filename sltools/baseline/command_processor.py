from importlib.metadata import version

from sltools.baseline.command_baseline import Command
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn


class CommandProcessor(Command):

    def __init__(self, commands: list):
        self.commands = commands
        self._registry = {}

        for cmd in self.commands:
            self._registry[cmd.get_name()] = cmd
            for alias in cmd.get_aliases():
                self._registry[alias] = cmd

    def get_name(self):
        return "root"

    def setup(self, parser):
        parser.add_argument('--version', action='version', version=version('sltools'))
        subparsers = parser.add_subparsers(dest='command', help=trn('Sub-commands available:'))

        for cmd in self.commands:
            log.debug(trn("Processing: %s") % cmd.get_name())
            cmd.setup(subparsers)

    def execute(self, args) -> {}:
        command_name = args.command
        command = self._registry.get(command_name)

        if command:
            log.debug(trn("Executing command: %s") % command_name)
            result = command.execute(args)
            command.display_result(result)
            return result
        else:
            log.error(trn("Command not found: %s") % command_name)
            return {}

    def display_result(self, result: {}):
        NotImplemented(trn("The method should not be used on the root command obj"))

    def man(self):
        NotImplemented(trn("The method should not be used on the root command obj"))

    def get_aliases(self) -> []:
        NotImplemented(trn("The method should not be used on the root command obj"))
