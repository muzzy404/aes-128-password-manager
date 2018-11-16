import aes.transformations as aes


def get_state_from_data(data):
    state = [[] for i in range(aes.R)]
    for row in range(aes.R):
        for column in range(aes.NB):
            state[row].append(data[row + aes.R * column])
    return state


def get_data_from_state(state):
    data = []
    for column in range(aes.NB):
        for row in range(aes.R):
            data.append(state[row][column])
    return data


def encrypt(data, key):
    """
    Encryption function.

    :param data: data to encrypt
    :type data: list of int
    :param key: master password
    :type key: str
    :return: encrypted data
    """
    state = get_state_from_data(data)

    key_schedule = aes.key_expansion(key)
    state = aes.add_round_key(state, key_schedule)

    for i in range(1, aes.NR):  # NR-1 rounds
        state = aes.sub_bytes(state)
        state = aes.shift_rows(state)
        state = aes.mix_columns(state)
        state = aes.add_round_key(state, key_schedule, round_number=i)

    # last round
    state = aes.sub_bytes(state)
    state = aes.shift_rows(state)
    state = aes.add_round_key(state, key_schedule, aes.NR)

    encrypted = get_data_from_state(state)
    return encrypted


def decrypt(data, key):
    state = get_state_from_data(data)
    key_schedule = aes.key_expansion(key)
    state = aes.add_round_key(state, key_schedule, aes.NR)

    for i in range(aes.NR - 1, 0, -1):
        state = aes.shift_rows(state, reverse=True)
        state = aes.sub_bytes(state, reverse=True)
        state = aes.add_round_key(state, key_schedule, round_number=i)
        state = aes.mix_columns(state, reverse=True)

    state = aes.shift_rows(state, reverse=True)
    state = aes.sub_bytes(state, reverse=True)
    state = aes.add_round_key(state, key_schedule)

    decrypted = get_data_from_state(state)
    return decrypted


def message_to_blocks(message, check_for_invalid=True):
    block_size = aes.R * aes.NB

    blocks = []
    block = []
    for symbol in message:
        if check_for_invalid:
            if symbol not in aes.VALID_SYMBOLS:
                raise Exception('Message includes unsupported symbol "{}".'.format(symbol))
        block.append(ord(symbol))
        if len(block) == block_size:
            blocks.append(block)
            block = []

    if len(block) < block_size:
        block.extend([aes.EMPTY_SYMBOL_CODE for i in range(len(block), block_size)])
    blocks.append(block)
    return blocks


def blocks_to_message(blocks):
    blocks[-1] = list(filter(lambda s: s != aes.EMPTY_SYMBOL_CODE, blocks[-1]))
    message = ''
    for block in blocks:
        for symbol in block:
            message += chr(symbol)
    return message



