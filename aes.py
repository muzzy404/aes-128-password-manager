import transformations as aes


def encrypt(data, key):
    """

    :param data: data to encrypt
    :type data: list of int
    :param key: master password
    :type key: str
    :return: encrypted data
    """
    state = [[] for i in range(aes.R)]
    for row in range(aes.R):
        for column in range(aes.NB):
            state[row].append(data[row + aes.R * column])

    key_schedule = aes.key_expansion(key)
    state = aes.add_round_key(state, key_schedule)

    for i in range(1, aes.NR):  # NR-1 rounds
        state = aes.syb_bytes(state)
        state = aes.shift_rows(state)
        state = aes.mix_columns(state)
        state = aes.add_round_key(state, key_schedule, round_number=i)

    # last round
    state = aes.syb_bytes(state)
    state = aes.shift_rows(state)
    state = aes.mix_columns(state)

    encrypted = []
    for column in range(aes.NB):
        for row in range(aes.R):
            encrypted.append(state[row][column])
    return encrypted


def decrypt(data, key):
    pass
