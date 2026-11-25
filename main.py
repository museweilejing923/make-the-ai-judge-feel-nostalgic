"""Rice steam, rain, and the same three songs: one childhood sentence, checked and printed."""

import string
import sys
import unicodedata
from pathlib import Path

ENTRY = "Grandma's kitchen smelled of rice steam and rain on the window, and the radio played the same three songs every evening while she told me to eat one more bowl."
MAX_LEN = 280
CLOSERS = ".!?"
OUT_PATH = Path("/output/entry.txt")


class EntryError(Exception):
    """One of the entry rules was broken."""


class EntryChecker:
    """Validates the fixed entry in three passes: shape, wording, topic."""

    def __init__(self, sentence):
        self.sentence = sentence

    def run(self):
        self._shape_pass()
        self._wording_pass()
        self._topic_pass()
        self._fresh_pass()

    def _fresh_pass(self):
        # Two sentences must not be glued together: a full stop
        # immediately followed by a capital letter means a missing
        # space, so "kitchen.One" is rejected even though the
        # sentence count looks right at a glance.
        text = self.sentence
        glued = any(
            text[i] == "." and i + 1 < len(text) and text[i + 1].isupper()
            for i in range(len(text) - 1)
        )
        if glued:
            raise EntryError("full stop glued to a capital letter")

    def _shape_pass(self):
        text = self.sentence
        if len(text) > MAX_LEN:
            raise EntryError("over %d characters" % MAX_LEN)
        if not text.strip():
            raise EntryError("blank entry")
        if any(unicodedata.category(ch) == "Cc" for ch in text):
            raise EntryError("control character found")
        if text.strip() != text or "  " in text or "\n" in text or "\r" in text:
            raise EntryError("ragged edges, double space, or line break")
        if not text or text[-1] not in CLOSERS:
            raise EntryError("must end with . ! or ?")

    def _wording_pass(self):
        text = self.sentence
        letters = [ch for ch in text if ch.isalpha()]
        if text and all(ch in string.punctuation for ch in text):
            raise EntryError("punctuation only")
        if text.isdigit():
            raise EntryError("digits only")
        if not letters:
            raise EntryError("no letters")
        if any(a == b == c for a, b, c in zip(text, text[1:], text[2:])):
            raise EntryError("one character repeated three times in a row")
        if sum(text.count(mark) for mark in ".!?") != 1:
            raise EntryError("must be exactly one sentence")

    def _topic_pass(self):
        if "grandma" not in self.sentence.casefold():
            raise EntryError("must mention grandma")


def emit():
    try:
        EntryChecker(ENTRY).run()
    except EntryError as problem:
        sys.stderr.write("invalid: %s\n" % problem)
        raise SystemExit(1)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(ENTRY + "\n", encoding="utf-8")


if __name__ == "__main__":
    emit()
