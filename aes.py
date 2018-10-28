import string
from tables import S_BOX, REVERSE_S_BOX, GF_MATRIX, REVERSE_GF_MATRIX

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
MAX_KEY_LENGTH = 16


def syb_bytes(state, reverse=False):
    """
    Non-linear substitution step where each byte is replaced with another according to a lookup table.

    :param state: data block to modify
    :type state: list of lists
    :param reverse:
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
    :param reverse:
    :return: shifted data block
    """
    for i in range(1, R):
        row = state[i]
        state[i] = row[i:] + row[:i - NB] if not reverse else row[-i:] + row[:NB - i]
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
    if MIN_KEY_LENGTH > len(key) > MAX_KEY_LENGTH:
        raise Exception('Key length is {}. '
                        'Required key length is {} or less symbols'.format(len(key), MAX_KEY_LENGTH))

    valid_symbols = list(string.punctuation + string.ascii_letters) + [str(num) for num in range(10)]
    if any(symbol not in valid_symbols for symbol in key):
        raise Exception('Key include invalid symbols.')

    if len(key) < R * NK:
        key += chr(0x01) * (R * NK - len(key))
    key_symbols = [ord(symbol) for symbol in key]

    key_schedule = [[] for i in range(R)]
    for row in range(R):
        for column in range(NK):
            key_schedule[row].append(key_symbols[row + R * column])

    # TODO: WIP


# TEST
# m_1 = [[0xdb, 0x13, 0x53, 0x45], [0xf2, 0x0a, 0x22, 0x5c], [0x01, 0x01, 0x01, 0x01], [0xc6, 0xc6, 0xc6, 0xc6]]
# print('m_1', m_1)
# m_2 = mix_columns(m_1)
# print('m_2', m_2)
# m_3 = mix_columns(m_2, True)
# print('m_3', m_3)
