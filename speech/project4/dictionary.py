from . import DATA_DIR, read_file
from .lextree import Trie


def dictionary_trie():
    dictionary = read_file(f"{DATA_DIR}dict_1.txt").split()
    dict_trie = Trie()
    for word in dictionary:
        dict_trie.insert(word)
    return dict_trie


def main() -> None:
    dict_trie = dictionary_trie()
    print(dict_trie)


main() if __name__ == "__main__" else None
