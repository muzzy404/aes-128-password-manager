""" Module with simple AES-128 test. """
from aes import aes

if __name__ == '__main__':
    message = "The Advanced Encryption Standard (AES), also known by its original name Rijndael\n" \
              "(Dutch pronunciation:, is a specification for the encryption of electronic data\n" \
              "established by the U.S. National Institute of Standards and Technology (NIST) in 2001.\n"

    blocks = aes.message_to_blocks(message)
    encrypted = []
    for block in blocks:
        encrypted.append(aes.encrypt(block, 'testpassword'))

    encrypted_message = aes.blocks_to_message(encrypted)
    blocks = aes.message_to_blocks(encrypted_message, check_for_invalid=False)

    decrypted = []
    for block in encrypted:
        decrypted.append(aes.decrypt(block, 'testpassword'))
    decrypted_message = aes.blocks_to_message(decrypted)

    print('original ({}):'.format(len(message)))
    print(message)
    print('\nencrypted ({}):'.format(len(encrypted_message)))
    print(encrypted_message)
    print('\ndecrypted ({}):'.format(len(decrypted_message)))
    print(decrypted_message)
