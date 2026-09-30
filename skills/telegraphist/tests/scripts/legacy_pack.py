"""Remove JSON whitespace, preserving string/number bytes; append no newline."""
import json
import os
import sys


# ponytail: 10 MiB input-size cap; use a reviewed streaming parser above it.
MAX_BYTES = 10 * 1024 * 1024


def reject_constant(value):
    raise ValueError("Nonstandard constant")


def unique_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate key")
    return None


def compact(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError("Input too large")
    text = raw.decode("utf-8")
    json.loads(text, parse_int=str, parse_float=str,
               parse_constant=reject_constant, object_pairs_hook=unique_keys)
    del text
    output = bytearray()
    in_string = escaped = False
    for byte in raw:
        if in_string:
            output.append(byte)
            if escaped:
                escaped = False
            elif byte == 92:  # backslash
                escaped = True
            elif byte == 34:  # quote
                in_string = False
        elif byte not in b' \t\r\n':
            output.append(byte)
            if byte == 34:
                in_string = True
    return output


if __name__ == "__main__":
    try:
        output = compact(sys.stdin.buffer.read(MAX_BYTES + 1))
    except (ValueError, RecursionError, OSError):
        print("pack: invalid JSON input", file=sys.stderr)
        sys.exit(1)
    try:
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
    except OSError:
        # Discard pending bytes so interpreter shutdown cannot retry failed output.
        with open(os.devnull, "wb") as sink:
            os.dup2(sink.fileno(), sys.stdout.fileno())
        print("pack: output error", file=sys.stderr)
        sys.exit(1)
