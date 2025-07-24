from abc import ABC
import re
from pybtex.database.input import bibtex
import sys
from jinja2 import Environment, FileSystemLoader


def is_good(s):
    if s.count('{') != s.count('}'):
        return False
    elif (s.count('"') - s.count('\"')) %2 != 0:
        return False
    else:
        return True
    
def find_matching_paren(s, i, braces=None):
    openers = braces or {"(": ")"}
    closers = {v: k for k, v in openers.items()}
    stack = []
    result = []

    if s[i] not in openers:
        raise ValueError(f"char at index {i} was not an opening brace")

    for ii in range(i, len(s)):
        c = s[ii]

        if c in openers:
            stack.append([c, ii])
        elif c in closers:
            if not stack:
                raise ValueError(f"tried to close brace without an open at position {i}")

            pair, idx = stack.pop()

            if pair != closers[c]:
                raise ValueError(f"mismatched brace at position {i}")

            if idx == i:
                return ii
    
    if stack:
        raise ValueError(f"no closing brace at position {i}")

    return result

def load_words_from_file(filepath: str) -> list:
    with open (filepath, 'r') as f:
        words = f.read().strip().split('\n')
    return words

TYPES_LIST = load_words_from_file("entry_types.txt")
KEYWORDS = load_words_from_file("keywords.txt")


class Bibliography(ABC):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.parser = None
        self.contents = None
        self.entries = None
        self.number_of_entries = None

        self._parse_bib_file()

    def _parse_bib_file(self) -> None:
        self.parser = bibtex.Parser()
        self.parsed_contents = self.parser.parse_file(self.filepath)
        self.entries = self.parsed_contents.entries
        self.number_of_entries = len(self.entries)

    # def _split_bib_file_into_entries(self) -> None:
    #     entries_strings = self.bib_file_contents.split("@")
    #     self.entries_strings = [
    #         entry for entry in entries_strings
    #         if entry not in ['', '\n']
    #     ]
    #     self.number_of_entries = len(self.entries_strings)

    def _process_entry_strings(self) -> None:
        self.entries = []
        for entry in self.entries_strings:
            self.entries.append(BibEntry(entry.strip()))

    def merge(self, AnotherBibliography) -> None:
        self._merge_bibliography(AnotherBibliography)

    def _merge_bibliography(self, AnotherBibliography) -> None:
        print(f"Current bibliography has {self.number_of_entries} entries.")

        count = 0

        for other_entry in AnotherBibliography.entries:
            if other_entry not in self.entries:
                self.entries[other_entry] = AnotherBibliography.entries[other_entry]
                count += 1
            elif self.entries[other_entry] != AnotherBibliography.entries[other_entry]:
                # self._merge_entry(other_entry, AnotherBibliography.entries[other_entry])
                different = 0
                for new_field in AnotherBibliography.entries[other_entry].fields:
                    if new_field not in self.entries[other_entry].fields:
                        if AnotherBibliography.entries[other_entry].fields[new_field] == '':
                            continue
                        else:
                            different = 1
                    elif self.entries[other_entry].fields[new_field] != AnotherBibliography.entries[other_entry].fields[new_field]:
                        different = 1
                
                if self.entries[other_entry].persons != AnotherBibliography.entries[other_entry].persons:
                    different = 1

                if different:
                    self.entries[f"{other_entry}_NEW"] = AnotherBibliography.entries[other_entry]
                    print(f"Resolve conflict in entry {other_entry}.")
                    count += 1
                else:
                    pass
            else:
                pass

        print(f"Merging added {count} entries from the new bibliography.")
        
        self.parsed_contents.entries = self.entries
        self.number_of_entries = len(self.entries)

        print(f"Current bibliography has {self.number_of_entries} entries.")

    def _merge_entry(self, entry_name, AnotherEntry) -> None:
        count = 0
        for new_field in AnotherEntry.fields:
            if new_field not in self.entries[entry_name].fields:
                if AnotherEntry.fields[new_field] != '':
                    self.entries[entry_name].fields[new_field] = AnotherEntry.fields[new_field]
                    count += 1
                else:
                    pass
            elif self.entries[entry_name].fields[new_field] != AnotherEntry.fields[new_field]:
                print(f"Differring field '{new_field}':")
                print(f"\tKept: {self.entries[entry_name].fields[new_field]}")
                print(f"\tRejected: {AnotherEntry.fields[new_field]}")
                pass

        if self.entries[entry_name].persons != AnotherEntry.persons:
            print(f"Different persons.")
            print(f"\tKept: {self.entries[entry_name].persons}")
            print(f"\tRejected: {AnotherEntry.persons}")
            pass

        if count > 0:
            print(f"Updated entry '{entry_name}' from new bibliography.")

    def to_file(
            self,
            filename: str = "bibliography.bib",
        ) -> None:

        self.paren_dict = {}

        for key in self.parsed_contents.entries:
            entry = self.parsed_contents.entries[key]

            title_bracket_flag = True

            if "title" in entry.fields.keys():
                if entry.fields["title"][0] == '{':
                    if find_matching_paren(entry.fields["title"], 0, {'{': '}'}) == len(entry.fields["title"]) - 1:
                        title_bracket_flag = False

            self.paren_dict[key] = title_bracket_flag
            
        env = Environment(
            loader=FileSystemLoader("templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self.template = env.get_template("bibliography.jinja")

        self.output = self.template.render(
            bibliography=self.parsed_contents.entries,
            parentheses=self.paren_dict,
        )

        with open(filename, "w") as output_file:
	        output_file.write(self.output)

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

        
