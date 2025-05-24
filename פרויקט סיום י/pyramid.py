from is_english import is_english_message
# checking if more than 70 precent of a message are words in english
from itertools import permutations
# making all combinations of numbers in length of the input number

def fill_pyramid_array_from_message(msg, key):
    """
    fills a pyramid array - an array with the input message, written in rows and input-key-length number of columns
    :param msg:     user input message for filling the pyramid array
    :param key:     user input key, its length will be the array's columns number
    :return:        the pyramid array
    """
    global num_of_rows
    msglen = len(msg)
    keylen = len(str(key))
    arr = [['' for x in range(keylen)] for y in range(msglen)]
    start = 0
    done = False
    row_length = 0
    for i in range(1, msglen):
        num_of_rows = i
        if done:
            break
        row_length += 1
        modulu = i % keylen
        if modulu == 1:
            row_length = 1
        col = 0
        for x in range(start, start + row_length):
            arr[i][col] = msg[x]
            if x == msglen - 1:
                done = True
                break
            start = x
            col += 1
        start += 1
    return arr

def get_encrypted_string_for_opposite_key(pyramid_array, reversed_key):
    """
    returns encrypted string by reading the pyramid_array column by column according to the reversed user input key
    :param pyramid_array: the pyramid array built from the user message and key input
    :param reversed_key:  the reversed user input key
    :return:              the encrypted string
    """
    concat = ''
    for x in reversed_key:
        actual_col = int(x) - 1
        for row in range(1, num_of_rows):
            if str(pyramid_array[row][actual_col]) != '':
                concat += str(pyramid_array[row][actual_col])
            else:
                concat += '$'
    return concat

def encrypt_pyramid(message, key):
    """
    validates its parameters
    calls two functions:
    first - fills the pyramid array
    second - returns the encrypted string
    :param message: the user message input for encrypting
    :param key:     the user key input for encrypting
    :return:        the encrypted string
    """
    if not(checking_parameters(message, key)[0]):
        return False
    # check that is only relevant for encrypt
    for i in message:
        if i == '$':
            return False, "text can not contain $ sign"
    pyramid_array = fill_pyramid_array_from_message(message, key)
    reversed_key = str(key)[::-1]
    print("the pyramid array")
    for n in range(1, num_of_rows):
        print(pyramid_array[n])
    return get_encrypted_string_for_opposite_key(pyramid_array, reversed_key)

def decrypt_pyramid(encrypted_message, key):
    """
    validates its parameters
    fills a pyramid shaped array with the encrypted message
    switches the columns according to the reversed user input key
    reads the updated array by rows
    returns decrypted string
    :param encrypted_message: the encrypted message
    :param key:               the user input key
    :return:                  the decrypted string
    """
    if not (checking_parameters(encrypted_message, key)[0]):
        return False
    decrypted = ""
    reversed_key = int(str(key)[::-1])
    num_rows = len(encrypted_message)//len(str(key))
    arr = [['' for x in range(len(str(key)))] for y in range(len(encrypted_message))]
    index = 0
    for i in range(len(str(key))):
        for j in range(num_rows):
            arr[j][i] = encrypted_message[index]
            index += 1

    updated_arr = [['' for x in range(len(str(key)))] for y in range(len(encrypted_message))]
    for j in range(len(str(key))):
        for i in range(num_rows):
            updated_arr[i][int(str(reversed_key)[j]) - 1] = arr[i][j]
    for i in range(num_rows):
        for j in range(len(str(key))):
            if updated_arr[i][j] != "$":
                decrypted += updated_arr[i][j]
    return decrypted

def get_secrets_permutations(key):
    """
    Prepare list of string secrets for key of transposition cipher
    secret is a combination of numbers from 1 to key in different order
    :param key: number that represent number of columns in transposition cipher
    :return: list of all possible secrets for specific transposition key
    """
    my_list = list(range(1, key+1))
    # Generate all permutations
    all_permutations = list(permutations(my_list))
    secrets = []
    for permutation in all_permutations:
        secrets.append("".join(str(num) for num in permutation))
    return secrets

def hack_pyramid(encrypted_message):
    """
    checks the decryption of the input message for different keys and returns the key
    for which the decrypted message is readable in English (if was found), and the decrypted message
    :param encrypted_message: the input encrypted message
    :return:                  either a message containing the found key and the decrypted message
                              or a message saying that such a key was not found
    """
    for key in range(2, 10):
        for secret in (get_secrets_permutations(key)):
            decrypted_msg = decrypt_pyramid(encrypted_message, secret)
            if is_english_message(decrypted_msg):
                return "decrypted message: " + decrypted_msg + ", optional key: " + str(secret)
    return "there is no possible key"

def checking_parameters(message, key):
    """
    Validates input parameters (only digits between 1-9, the digits should not be higher than the key's length,
    there shouldn't be digits duplications, the key shouldn't be longer than 9), the key cannot be 1, the message must be filled
    :param message: user input message
    :param key:     user input key
    :return:        True for success, False for failure and error message
    """
    if message == "":
        return False, "the text to encrypt/decrypt must be filled"
    for i in str(key):
        if not(i.isnumeric()) or int(i) == 0:
            return False, "Key must contain only digits between 1 and 9"

    for i in str(key):
        if int(i) > len(str(key)):
            return False, "at least one of the key's digits is higher than its length"

    for i in range(len(str(key))):
        for j in range(i + 1, len(str(key))):
            if str(key)[i] == str(key)[j]:
                return False, "the key contains duplications"

    if key == 1:
        return False, "key cannot be 1"

    if len(str(key)) > 9:
        return False, "Key must be at most 9 digits long."

    return True, None

# *******************************************************************

'''
a general explanation
a pyramid array is built for example, from string "abcdefghijklmnopqrstu" and key of 5 digits, as follows
a
bc
def
ghij
klmno
p
qr
stu
'''

if __name__ == '__main__':
    print("Enter your message for encryption: ")
    input_message = input()
    try:
        print("Enter your key for encryption: ")
        input_key = int(input())
    except:
        print("please enter only digits for the key")
        exit()

    print("encrypt: \nmessage: " + input_message)
    encrypted_msg = encrypt_pyramid(input_message, input_key)
    if not encrypted_msg:
        print("parameters validation failed: " + checking_parameters(input_message, input_key)[1])
    elif not encrypted_msg[0]:
        print(encrypted_msg[1])
    else:
        print("key: " + str(input_key) + ", reversed_key: " + str(str(input_key)[::-1]) + ", encrypted message: " + encrypted_msg)
        print("\ndecrypt:")
        print("decrypted message : " + str(decrypt_pyramid(encrypt_pyramid(input_message, input_key), input_key)))

    print("\nexample:")
    print("message: " + "how are you this morning ?")
    print("decrypt encrypted message: " + str(decrypt_pyramid(encrypt_pyramid("how are you this morning ?", 3124), 3124)))