from tables import S_BOX, REVERSE_S_BOX
# state = [[], [], [], []]
#
#           1   2   3   NB
#         [[a1, b1, c1, d1],  | 1
#          [a2, b2, c2, d2],  | 2
#          [a3, b3, c3, d3],  | 3
#          [a4, b4, c4, d4]]  | 4 = rows number

R = 4    # rows number

NB = 4   # columns number (number of 32 bit words), NB = 4 for AES
NK = 4   # key length in 32 bit word, NK = 4/6/8 for AES
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

    :param state:
    :param reverse:
    :return:
    """
    for i in range(1, R):
        row = state[i]
        state[i] = row[i:] + row[:i-NB] if not reverse else row[-i:] + row[:NB-i]
    return state
