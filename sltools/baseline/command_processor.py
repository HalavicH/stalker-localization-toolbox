from sltools.baseline.command_baseline import Command
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn
from importlib.metadata import version


class CommandProcessor(Command):

    def __init__(self, commands: []):
        self.commands = commands
        self._registry = {}

        for cmd in self.commands:
            cmd: Command
            name = cmd.get_name()
            aliases = cmd.get_aliases()
            aliases.append(name)

            self._registry[aliases] = cmd

    def get_name(self):
        return "root"

    def setup(self, parser):
        parser.add_argument('--version', action='version', version=version('sltools'))
        subparsers = parser.add_subparsers(dest='command', help=trn('Sub-commands available:'))

        for cmd in self._registry.values():
            log.debug("Processing: " + cmd.get_name())
            cmd.setup(subparsers)

    def execute(self, args) -> {}:
        for cmd_names in self._registry:
            if args.command not in cmd_names:
                continue

            log.debug("Found command. All aliases: %s" % cmd_names)
            command: Command = self._registry[cmd_names]

            result = command.execute(args)
            command.display_result(result)

            # for further processing if needed
            return result

    def display_result(self, result: {}):
        NotImplemented(trn("The method should not be used on the root command obj"))

    def man(self):
        NotImplemented(trn("The method should not be used on the root command obj"))
