from bibliography import Bibliography

from pybtex.database.input import bibtex

def is_good(s):
    if s.count('{') != s.count('}'):
        return False
    elif (s.count('"') - s.count('\"')) %2 != 0:
        return False
    else:
        return True

if __name__ == "__main__":
    # biblio = Bibliography("../topology_bibtex/TopoBiblio.bib")

    # print(is_good(biblio.bib_file_contents))

    parser = bibtex.Parser()
    bib_data = parser.parse_file("../topology_bibtex/topology.bib")

    print(len(bib_data.entries))
