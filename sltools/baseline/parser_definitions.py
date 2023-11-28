import argparse

from rich_argparse import RichHelpFormatter

from sltools.utils.lang_utils import trn
from sltools.utils.misc import check_for_update


class CustomHelpFormatter(RichHelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position=40, width=120)


class ExtendedHelpParser(argparse.ArgumentParser):
    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # Add version check
        formatter.add_text(check_for_update())
        # determine help from format above
        return formatter.format_help()


class BooleanAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() in ['true', 't', 'yes', 'y', '1']:
            setattr(namespace, self.dest, True)
        elif values.lower() in ['false', 'f', 'no', 'n', '0']:
            setattr(namespace, self.dest, False)
        else:
            parser.error(f"Invalid value for {self.dest}: {values}")


def add_git_override_arguments(parser):
    parser.add_argument('--allow-no-repo', action='store_true', default=False,
                        help=trn('Allow operations without Git repository'))
    parser.add_argument('--allow-dirty', action='store_true', default=False,
                        help=trn('Allow operations on dirty Git repositories'))
    parser.add_argument('--allow-not-tracked', action='store_true', default=False,
                        help=trn('Allow operations on untracked by Git files'))
