from abc import abstractmethod, ABC

from argparse import ArgumentParser

from sltools.baseline.parser_definitions import CustomHelpFormatter
from sltools.utils.lang_utils import trn


class Command(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_aliases(self) -> list:
        pass

    @abstractmethod
    def setup(self, parser):
        pass

    @abstractmethod
    def execute(self, args) -> dict:
        pass

    @abstractmethod
    def display_result(self, result: dict):
        pass

    def man(self) -> str:
        return "No man page for command '%s'!" % self.get_name()


class AbstractCommand(Command, ABC):
    def get_aliases(self) -> list:
        return []

    def setup(self, parser):
        _parser = self.create_cmd_parser(parser)
        self._setup_parser_args(_parser)

    @abstractmethod
    def _setup_parser_args(self, parser):
        pass

    @abstractmethod
    def _get_help(self) -> str:
        pass

    def create_cmd_parser(self, subparsers) -> ArgumentParser:
        parser_ve = subparsers.add_parser(self.get_name(), aliases=self.get_aliases(),
                                          formatter_class=CustomHelpFormatter,
                                          help=self._get_help())
        return parser_ve

    @staticmethod
    def __add_git_override_arguments(parser):
        parser.add_argument('--allow-no-repo', action='store_true', default=False,
                            help=trn('Allow operations without Git repository'))
        parser.add_argument('--allow-dirty', action='store_true', default=False,
                            help=trn('Allow operations on dirty Git repositories'))
        parser.add_argument('--allow-not-tracked', action='store_true', default=False,
                            help=trn('Allow operations on untracked by Git files'))
