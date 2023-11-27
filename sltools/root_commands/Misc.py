import requests
from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.utils.colorize import cf_red
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table, generate_gradient_usage_bar


class Misc(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "misc"

    def _get_help(self) -> str:
        return trn('Misc housekeeping and experimental commands')

    def _setup_parser_args(self, parser):
        parser.add_argument('--check-deepl-tokens-usage',
                                 nargs='+',  # '+' means "at least one"
                                 help=trn('Checks DeepL tokens quota (provide token list separated by the space'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        pass

    @staticmethod
    def check_deepl_tokens_usage(token_list):
        columns = [trn("Token"), trn("Plan"), trn("Used"), trn("Available"), trn("Used %")]
        table = create_table(columns, title=trn("DeepL Token Usage"), border_style="blue")

        api_url = 'https://api-free.deepl.com/v2/usage'

        for token in token_list:
            headers = {"Authorization": f"DeepL-Auth-Key {token}"}

            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                json_data = response.json()

                if 'character_count' in json_data and 'character_limit' in json_data:
                    plan = json_data['character_limit']
                    used = json_data['character_count']
                    used_percentage = (used / plan) * 100 if plan != 0 else 0
                    available = plan - used
                    table.add_row(
                        token,
                        f"{plan:,}".replace(",", " ").rjust(7),
                        f"{used:,}".replace(",", " ").rjust(7),
                        f"{available:,}".replace(",", " ").rjust(7),
                        generate_gradient_usage_bar(used_percentage, 30)
                    )
                else:
                    table.add_row(token, cf_red(trn("Error")), "N/A", "N/A", "N/A")

            except requests.exceptions.RequestException as e:
                table.add_row(token, cf_red(trn("Error")), "N/A", "N/A", "N/A")

        get_console().print(table)

    def execute(self, args) -> dict:
        if args.check_deepl_tokens_usage is not None:
            self.check_deepl_tokens_usage(args.check_deepl_tokens_usage)

        return {}

    # Displaying
    ############
    def display_result(self, result: dict):
        pass
