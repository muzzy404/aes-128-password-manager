import string
from tables import S_BOX, REVERSE_S_BOX, GF_MATRIX, REVERSE_GF_MATRIX, RCON

# state = [[], [], [], []]
#
#           1   2   3   NB
#         [[a1, b1, c1, d1],  | 1
#          [a2, b2, c2, d2],  | 2
#          [a3, b3, c3, d3],  | 3
#          [a4, b4, c4, d4]]  | 4 = rows number (R)
# https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
# https://habr.com/post/212235/

R = 4    # rows number

NB = 4   # columns number (number of 32 bit words), NB = 4 for AES
NK = 4   # key length in 32 bit word, NK = 4/6/8 for AES
NR = 10  # cypher rounds, NR = 10/12/14 for AES

MIN_KEY_LENGTH = 6
MAX_KEY_LENGTH = R * NK
VALID_SYMBOLS = list(string.printable)
EMPTY_SYMBOL_CODE = 0x01


def sub_bytes(state, reverse=False):
    """
    Non-linear substitution step where each byte is replaced with another according to a lookup table.

    :param state: data block to modify
    :type state: list of lists
    :param reverse: direction of transformation
    :type reverse: bool
    :return: modified data block
    """
    table = S_BOX if not reverse else REVERSE_S_BOX

    for i in range(R):
        for j in range(NB):
            row = state[i][j] // 0x10
            column = state[i][j] % 0x10
            state[i][j] = table[row][column]
    return state


def shift_rows(state, reverse=False):
    """
    Transposition step where all rows of the state except first one are shifted cyclically a certain number of steps.

    :param state: data block to modify
    :type state: list of lists
    :param reverse: direction of transformation
    :type reverse: bool
    :return: shifted data block
    """
    for i in range(1, R):
        row = state[i]
        # left shift or right shift
        state[i] = row[i:] + row[:i] if not reverse else row[-i:] + row[:-i]
    return state


def gf256_mul(a, b):
    """
    Two numbers multiplication in the GF(256).
    https://en.wikipedia.org/wiki/Finite_field_arithmetic#C_programming_example
    https://en.wikipedia.org/wiki/Rijndael_MixColumns

    :param a: first number
    :param b: second number
    :return: result of multiplication
    """
    result = 0x0
    while a and b != 0:
        if b % 2 == 1:  # if b is odd
            result ^= a  # add corresponding a to result
        not_shifted_a = a
        a <<= 1  # multiply by 2
        if not_shifted_a & 0x80 != 0:  # if not_shifted_a >= 128, a will be overflowed
            # xor with the primitive polynomial: x^8 + x^4 + x^3 + x + 1
            a ^= 0x11b  # (0b100011011 = 0x11b = 283)
        b >>= 1  # divide b to 2
    return result


def mix_columns(state, reverse=False):
    """
    Mix columns function. Transformation in GF(256) Galua filed.
    :param state: data block to modify
    :param reverse: direction of transformation
    :return: result of transformation for state
    """
    mul = gf256_mul
    matrix = GF_MATRIX if not reverse else REVERSE_GF_MATRIX
    for i in range(NB):
        column = []
        for row in matrix:
            cell = mul(row[0], state[0][i])
            for j in range(1, len(row)):
                cell ^= mul(row[j], state[j][i])
            column.append(cell)
        for j in range(len(column)):
            state[j][i] = column[j]
    return state


def key_expansion(key):
    """
    Generation of round keys.

    :param key: master password
    :type key: str
    :return: key schedule - round keys
    """
    if not (MIN_KEY_LENGTH <= len(key) <= MAX_KEY_LENGTH):
        msg = 'Key length is {}. Required key length is ' \
              '{}-{} symbols'.format(len(key), MIN_KEY_LENGTH, MAX_KEY_LENGTH)
        raise Exception(msg)

    if any(symbol not in VALID_SYMBOLS for symbol in key):
        raise Exception('Key includes invalid symbols.')

    if len(key) < R * NK:
        key += chr(EMPTY_SYMBOL_CODE) * (R * NK - len(key))
    key_symbols = [ord(symbol) for symbol in key]

    key_schedule = [[] for i in range(R)]
    for row in range(R):
        for column in range(NK):
            key_schedule[row].append(key_symbols[row + R * column])

    # by NB columns for each of NR + 1 rounds
    for i in range(NK, NB * (NR + 1)):
        if i % NK == 0:  # multiple of NB
            # left shift for previous
            column = [key_schedule[row][i - 1] for row in range(R)]
            column = column[1:] + column[:1]
            # replace elements according S_BOX
            for j in range(len(column)):
                row = column[j] // 0x10
                col = column[j] % 0x10
                column[j] = S_BOX[row][col]
            for row in range(R):
                a = key_schedule[row][i - NK]
                b = column[row]
                c = RCON[row][i/NK - 1]
                key_schedule[row].append(a ^ b ^ c)
        else:
            for row in range(R):
                a = key_schedule[row][i - NK]
                b = key_schedule[row][i - 1]
                key_schedule[row].append(a ^ b)
    return key_schedule


def add_round_key(state, key_schedule, round_number=0):
    """
    Addition of round key to state.

    :param state: data block to modify
    :param key_schedule: round keys from key_expansion
    :param round_number: number of round
    :return: result of transformation for state
    """
    for i in range(NK):
        for j in range(R):
            state[j][i] ^= key_schedule[j][NB * round_number + i]
    return state
