from abc import ABC
import re


def load_words_from_file(filepath: str) -> list:
    with open (filepath, 'r') as f:
        words = f.read().strip().split('\n')
    return words

TYPES_LIST = load_words_from_file("entry_types.txt")
KEYWORDS = load_words_from_file("keywords.txt")


class Bibliography(ABC):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.bib_file_contents = None
        self.entries_strings = None
        self.number_of_entries = None
        self.entries = None
        self.entry_type = None
        self.entry_key = None

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

    def _process_entry_strings(self) -> None:
        self.entries = []
        for entry in self.entries_strings:
            self.entries.append(BibEntry(entry.strip()))

    def merge(self, AnotherBib) -> None:
        self._merge_with_another(AnotherBib)

    def _merge_with_another(self, AnotherBib) -> None:
        pass


class BibEntry(ABC):
    def __init__(self, entry_string: str) -> None:
        self.entry_string = entry_string
        if self.entry_string[-1] == '}':
            raise IndexError("Entry string is not closed by '}'")

        self.entry_type = None
        self.key = None
        
    def _separate_entry_elements(self) -> None:
        entry_type, entry_body = self.entry_string[:-1].split(
            sep = '{',
            maxsplit = 1,
        )
        if entry_type.upper() not in TYPES_LIST:
            raise Exception(f"Unknown entry type: {entry_type}")
        
        self.entry_type = entry_type.upper()

        entry_key, pairs_str = entry_body.split(sep=',', maxsplit=1)
        self.entry_key = entry_key
        pairs_str = re.sub('\s+', ' ', pairs_str)

        rest_of_pairs_str = pairs_str
        while rest_of_pairs_str != "":
            keyword, pairs_str_remainder = pairs_str_remainder.split(
                sep = '=',
                maxsplit = 1,
            )

        
