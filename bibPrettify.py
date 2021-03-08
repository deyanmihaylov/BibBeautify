#!/usr/bin/python3

import argparse
import sys
import re

def find_parens(s):
    toret = {}
    pstack = []

    for i, c in enumerate(s):
        if c == '{':
            pstack.append(i)
        elif c == '}':
            if len(pstack) == 0:
                raise IndexError("No matching closing parens at: " + str(i))
            toret[pstack.pop()] = i

    if len(pstack) > 0:
        raise IndexError("No matching opening parens at: " + str(pstack.pop()))

    return toret

KEYWORDS = [
    "author",
    "title",
    "file",
    "journal",
    "volume",
    "edition",
    "number",
    "version",
    "year",
    "month",
    "timestamp",
    "number",
    "pages",
    "eid",
    "doi",
    "eprint",
    "archiveprefix",
    "primaryclass",
    "slaccitation",
    "howpublished",
    "publisher",
    "keywords",
    "collaboration",
    "address",
    "url",
    "bdsk-url-1",
    "booktitle",
    "reportnumber",
    "note",
    "series",
    "editor",
    "adsurl",
    "biburl",
    "adsnote",
    "added-at",
    "date-added",
    "date-modified",
    "numpages",
    "interhash",
    "intrahash",
]

TYPES_LIST = [
    "ARTICLE",
    "BOOK",
    "INPROCEEDINGS",
    "INCOLLECTION",
    "SOFTWARE",
    "MISC",
    "OTHER",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make a bib file pretty')
    parser.add_argument('path', metavar='p', type=str, help='path to the .bib file')

    args = parser.parse_args()

    bib_file = open(args.path, 'r')
    bib_filecontents = bib_file.read()
    bib_file.close()

    entries_strings = bib_filecontents.split("@")

    output_entry_list = []

    c = 0

    for entry_string in entries_strings:
        c += 1

        if entry_string == "":
            continue
        elif entry_string.strip()[-1] != "}":
            continue

        entry_type, entry_body = entry_string.split(
            sep="{",
            maxsplit=1,
        )

        if entry_type.upper() not in TYPES_LIST:
            print("UNKNOWN TYPE:", entry_type.upper())
            exit()

        output_entry_type = entry_type.upper()

        entry_name, entry_details = entry_body.split(
            sep=",",
            maxsplit=1,
        )

        output_entry_name = entry_name

        entry_details = entry_details[0:entry_details.rfind("}")]

        entry_details = re.sub(
            '\s+',
            ' ',
            entry_details,
        )

        output_entry_details_list = []

        rest_of_entry = entry_details

        while rest_of_entry != "":
            entry_keyword, entry_remainder = rest_of_entry.split(
                sep="=",
                maxsplit=1,
            )

            entry_keyword = entry_keyword.strip()

            if entry_keyword.lower() not in KEYWORDS:
                print("UNKNOWN KEYWORD: ", entry_keyword.lower())
                exit()

            entry_remainder = entry_remainder.strip()

            if entry_remainder[0] == '"':
                entry_val, rest_of_entry = entry_remainder[1:].split(
                    sep='"',
                    maxsplit=1,
                )
            elif entry_remainder[0] == '{':
                curly_brackets = find_parens(entry_remainder)

                entry_val = entry_remainder[1:curly_brackets[0]]
                rest_of_entry = entry_remainder[curly_brackets[0]+1:]
            else:
                if "," in entry_remainder:
                    entry_val, rest_of_entry = entry_remainder.split(
                        sep=',',
                        maxsplit=1,
                    )
                else:
                    entry_val = entry_remainder
                    rest_of_entry = ""

            rest_of_entry = rest_of_entry.strip()

            if len(rest_of_entry) > 0:
                if rest_of_entry[0] == ",":
                    rest_of_entry = rest_of_entry[1:]

            rest_of_entry = rest_of_entry.strip()

            output_entry_details_list.append(
                f"\t{entry_keyword} = \"{entry_val}\",\n"
            )

        output_entry_list.append(
            f"""@{output_entry_type}{{{output_entry_name},\n{''.join(output_entry_details_list)}}}"""
        )

    print('\n\n'.join(output_entry_list))

    # output_bib_file = open("./main.bib", 'w')
    # output_bib_file.write('\n\n'.join(output_entry_list))
    # output_bib_file.close()
