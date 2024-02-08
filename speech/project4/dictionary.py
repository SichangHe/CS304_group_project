from speech.project4 import DATA_DIR, read_lines_stripped
from speech.project4.lextree import Trie


def dictionary_trie():
    dictionary = read_lines_stripped(f"{DATA_DIR}dict_1.txt")
    dict_trie = Trie()
    for word in dictionary:
        dict_trie.insert(word)
    return dict_trie


def main() -> None:
    dict_trie = dictionary_trie()
    print(dict_trie)


main() if __name__ == "__main__" else None
