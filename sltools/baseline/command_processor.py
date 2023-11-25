from sltools.baseline.command_baseline import Command
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn
from importlib.metadata import version


class CommandProcessor(Command):

    def __init__(self, commands: []):
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

        for cmd in set(self._registry.values()):
            log.debug("Processing: " + cmd.get_name())
            cmd.setup(subparsers)

    def execute(self, args) -> {}:
        command_name = args.command
        command = self._registry.get(command_name)

        if command:
            log.debug(f"Executing command: {command_name}")
            result = command.execute(args)
            command.display_result(result)
            return result
        else:
            log.error(f"Command not found: {command_name}")
            return {}

    def display_result(self, result: {}):
        NotImplemented(trn("The method should not be used on the root command obj"))

    def man(self):
        NotImplemented(trn("The method should not be used on the root command obj"))

    def get_aliases(self) -> []:
        NotImplemented(trn("The method should not be used on the root command obj"))

