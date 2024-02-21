"""Unrestricted number of digits."""

from speech.project5.phone_rand import build_digit_hmms

DIGIT_STRINGS = [
    "911385",
    "826414052002",
    "8212176342",
    "7343332190377",
    "2212",
    "123456",
    "6890372344",
    "72184347924",
    "55555",
    "37274921",
]


def main() -> None:
    digit_hmms = build_digit_hmms()
    # TODO: Determine the  optimal insertion penalty empirically


main() if __name__ == "__main__" else None
