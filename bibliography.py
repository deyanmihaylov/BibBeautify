from abc import ABC


class Bibliography(ABC):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.bib_file_contents = None
        self.entries_strings = None
        self.number_of_entries = None

    def _read_bib_file(self) -> None:
        with open(self.filepath, 'r') as bib_file:
            self.bib_file_contents = bib_file.read()

    def _split_bib_file_into_entries(self) -> None:
        entries_strings = self.bib_file_contents.split("@")
        self.entries_strings = [
            entry for entry in entries_strings
            if entry not in ['', '\n']
        ]
        self.number_of_entries = len(self.entries_strings)

        
