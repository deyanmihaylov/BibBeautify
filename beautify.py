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

def find_occurrences(s, ch):
    return [i for i, c in enumerate(s) if c == ch]

def is_good(s):
    if s.count('{') != s.count('}'):
        return False
    elif (s.count('"') - s.count('\"')) %2 != 0:
        return False
    else:
        return True

def undress_value(val):
    if len(val) >= 2:
        if val[0] == '"' and val[-1] == '"':
            val = val[1:-1]

    if len(val) >= 2:
        if val[0] == '{' and val[-1] == '}':
            if val[1:].find('{') < val[1:].find('}'):
                val = val[1:-1]
                
    return val

def load_words_from_file(filepath: str) -> list:
    with open (filepath, 'r') as f:
        words = f.read().strip().split('\n')
    return words

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make a bib file pretty")
    parser.add_argument(
        "path",
        metavar='p',
        type=str,
        help="Path to the .bib file",
    )

    args = parser.parse_args()
    
    TYPES_LIST = load_words_from_file("entry_types.txt")
    KEYWORDS = load_words_from_file("keywords.txt")

    with open(args.path, 'r') as bib_file:
        bib_filecontents = bib_file.read().strip()

    # check that file has consistent use of curly brackets
    if not is_good(bib_filecontents):
        print("Possible runaway string.")
        sys.exit()

    # split file into separate entries
    entries_strings = bib_filecontents.split("@")
    entries_strings = [entry for entry in entries_strings if entry not in ['', '\n']]

    output_entry_list = []

    c = 0

    for entry_string in entries_strings:
        c += 1

        if entry_string == "":
            continue
        elif '{' not in entry_string and '}' not in entry_string:
            print("issue")
            exit()

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
        c = 0
        while rest_of_entry != "":
            c += 1
            equal_sign_idx = rest_of_entry.find('=')
            entry_keyword = rest_of_entry[0:equal_sign_idx].strip()
            # if '{' in entry_keyword:
            if entry_keyword.lower() not in KEYWORDS:
                print("UNKNOWN KEYWORD: ", entry_keyword.lower())
                exit()
            remainder_of_entry = rest_of_entry[equal_sign_idx+1:]
            N = remainder_of_entry.count('=')
            if N == 0:
                entry_value = remainder_of_entry.strip()
                rest_of_entry = ""
            else:
                for i in range(N):
                    candidate_value_and_next_keyword = remainder_of_entry[:remainder_of_entry.find('=')]
                    if ',' not in candidate_value_and_next_keyword:
                        if i == N - 1:
                            entry_value = remainder_of_entry
                            remainder_of_entry = ""
                        else:
                            continue
                    else:
                        candidate_value, candidate_keyword = candidate_value_and_next_keyword.rsplit(',', maxsplit=1)
                        if is_good(candidate_value) and candidate_keyword.strip().lower() in KEYWORDS:
                            entry_value = candidate_value.strip()
                            remainder_of_entry = remainder_of_entry[len(candidate_value)+1:]
                            break
                
                rest_of_entry = remainder_of_entry

            entry_value = undress_value(entry_value)

            output_entry_details_list.append(
                f"\t{entry_keyword} = \"{entry_value}\",\n"
            )

        output_entry_list.append(
            f"""@{output_entry_type}{{{output_entry_name},\n{''.join(output_entry_details_list)}}}"""
        )

    print('\n\n'.join(output_entry_list))

    # output_bib_file = open("./main.bib", 'w')
    # output_bib_file.write('\n\n'.join(output_entry_list))
    # output_bib_file.close()
