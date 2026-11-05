"""Flag instruction-like customer notes. Notes are data; this only detects, never obeys."""
import re
import unicodedata

_RULES = [
    ("override phrase",  r"\b(ignore|disregard|forget|override|bypass)\b(\W+\w+){0,3}?\W+(rules?|instructions?|prompts?|system|previous|above)\b"),
    ("role instruction", r"\b(you are now|act as|new instructions|system prompt)\b"),
    ("price directive",  r"\b(quote|charge|price|bill)\b[^.]{0,30}?(s?\$|sgd)\s?\d+(\.\d+)?(\s*(a|per|/)\s*box(es)?)?"),
    ("discount demand",  r"\b(discount|for free|waive\w*|\d+\s?% off|no gst|no delivery fee)\b"),
]


def check_note(note):
    """Return a list of reasons; empty means the note is not instruction-like."""
    text = " ".join(unicodedata.normalize("NFKC", note or "").lower().split())
    return [f'{label}: "{m.group(0)}"' for label, pattern in _RULES if (m := re.search(pattern, text))]
