from abc import ABC


class Bibliography(ABC):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.bib_file_contents = None

    def _read_bib_file(self) -> None:
        with open(self.filepath, 'r') as bib_file:
            self.bib_file_contents = bib_file.read()
        
