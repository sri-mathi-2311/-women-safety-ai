"""Console logging that survives Windows cp1252 / legacy stdout encodings."""

import sys


def log(*args, **kwargs) -> None:
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        try:
            print(msg.encode(enc, errors="replace").decode(enc, errors="replace"))
        except Exception:
            print(msg.encode("ascii", errors="replace").decode("ascii"))
