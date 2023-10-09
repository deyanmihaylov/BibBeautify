from abc import ABC


class Bibliography(ABC):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def _read_bib_file(self) -> None:
        pass
    