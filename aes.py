from sys import getsizeof

from tables import S_BOX, REVERSE_S_BOX

# state = [[], [], [], []]
#
#           1   2   3   NB
#         [[a1, b1, c1, d1],  | 1
#          [a2, b2, c2, d2],  | 2
#          [a3, b3, c3, d3],  | 3
#          [a4, b4, c4, d4]]  | 4 = rows number
# https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
# https://habr.com/post/212235/

R = 4  # rows number

NB = 4  # columns number (number of 32 bit words), NB = 4 for AES
NK = 4  # key length in 32 bit word, NK = 4/6/8 for AES
NR = 10  # cypher rounds, NR = 10/12/14 for AES


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
    col = range(R)
    for i in range(NB):
        if not reverse:
            col[0] = mul(0x02, state[0][i]) ^ mul(0x03, state[1][i]) ^ state[2][i] ^ state[3][i]
            col[1] = state[0][i] ^ mul(0x02, state[1][i]) ^ mul(0x03, state[2][i]) ^ state[3][i]
            col[2] = state[0][i] ^ state[1][i] ^ mul(0x02, state[2][i]) ^ mul(0x03, state[3][i])
            col[3] = mul(0x03, state[0][i]) ^ state[1][i] + state[2][i] ^ mul(0x02, state[3][i])
        else:
            col[0] = mul(0x0e, state[0][i]) ^ mul(0x0b, state[1][i]) ^ mul(0x0d, state[2][i]) ^ mul(0x09, state[3][i])
            col[1] = mul(0x09, state[0][i]) ^ mul(0x0e, state[1][i]) ^ mul(0x0b, state[2][i]) ^ mul(0x0d, state[3][i])
            col[2] = mul(0x0d, state[0][i]) ^ mul(0x09, state[1][i]) ^ mul(0x0e, state[2][i]) ^ mul(0x0b, state[3][i])
            col[3] = mul(0x0b, state[0][i]) ^ mul(0x0d, state[1][i]) ^ mul(0x09, state[2][i]) ^ mul(0x0e, state[3][i])
        for j in range(R):
            state[j][i] = col[j]

    return state
