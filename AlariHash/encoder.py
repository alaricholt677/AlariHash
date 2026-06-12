# alarihash/encoder.py

def normalize_input(s: str) -> str:
    return " ".join(s.lower().split())


def text_to_binary(s: str) -> str:
    return "".join(format(ord(c), "08b") for c in s)


def scramble_once(binary: str, round_index: int) -> str:
    out = []
    shift = (7 + round_index * 3) % len(binary) or 1

    for i in range(len(binary)):
        a = int(binary[i])
        b = int(binary[(i + shift) % len(binary)])
        c = int(binary[(i + len(binary) - shift) % len(binary)])
        bit = (a ^ b ^ c) & 1
        out.append(str(bit))

    return "".join(out)


def multi_round_scramble(binary: str, rounds: int) -> str:
    current = binary
    for r in range(rounds):
        current = scramble_once(current, r)
    return current


def rotate_left(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def mix_chunk(chunk: str) -> int:
    acc = 0
    for i, ch in enumerate(chunk):
        bit = 1 if ch == "1" else 0
        acc ^= (bit << (i % 31))
        acc = rotate_left(acc, (i % 5) + 1)
    return acc & 0xFFFFFFFF


def chunk_and_mix(binary: str, block_size: int) -> list[int]:
    blocks = []
    for i in range(0, len(binary), block_size):
        chunk = binary[i:i + block_size]
        blocks.append(mix_chunk(chunk))
    return blocks


def fold_blocks(blocks: list[int]) -> int:
    state = 0x9E3779B9  # golden ratio constant

    for i, v in enumerate(blocks):
        state ^= v
        state = (state + ((v << 5) - (v >> 3))) & 0xFFFFFFFF
        rot = (i % 13) + 3
        state = rotate_left(state, rot)
        state ^= (state >> 11)

    return state & 0xFFFFFFFF


def avalanche_mix(x: int) -> int:
    x ^= x >> 15
    x = (x * 0x85EBCA6B) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0xC2B2AE35) & 0xFFFFFFFF
    x ^= x >> 16
    return x & 0xFFFFFFFF


def alari_encode(text: str) -> str:
    text = normalize_input(text)
    binary = text_to_binary(text)
    scrambled = multi_round_scramble(binary, 5)
    blocks = chunk_and_mix(scrambled, 64)
    state = fold_blocks(blocks)
    final_int = avalanche_mix(state)
    hex_value = format(final_int, "016x")
    return f"alaricholt677.encoded${hex_value}"
