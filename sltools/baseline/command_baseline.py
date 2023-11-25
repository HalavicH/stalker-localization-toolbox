from abc import abstractmethod, ABC


class Command(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    def get_aliases(self) -> []:
        return []

    @abstractmethod
    def append_parser(self, parser):
        pass

    @abstractmethod
    def execute(self, args) -> {}:
        pass

    @abstractmethod
    def display_result(self, result: {}):
        pass

    def man(self) -> str:
        return "No man page for command '%s'!" % self.get_name()

