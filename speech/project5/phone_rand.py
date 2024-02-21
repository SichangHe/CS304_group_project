"""Recognize 25 valid random telephone numbers and report accuracy.
Run as `python3 -m speech.project5.phone_rand`."""

TELEPHONE_NUMBERS = [
    "8765",
    "2356",
    "4198",
    "7432",
    "5321",
    "6214",
    "8743021",
    "3156",
    "9821",
    "7245981",
    "1367",
    "5432",
    "2198473",
    "8976",
    "4298513",
    "6532",
    "5189",
    "9271564",
    "7345",
    "6291087",
    "4821",
    "7698432",
    "5412968",
    "8654123",
    "2371098",
]


def recording_for_number(number: str) -> str:
    """Return the recording file for the given number."""
    return f"recordings/{number}.wav"
