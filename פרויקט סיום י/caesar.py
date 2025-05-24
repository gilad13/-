import is_english


def cs_encrypt(key, message):
    """
    Encrypts a message using Caesar cipher with the given key.
    Parameters:
        key (int): The number of positions to shift each letter.
        message (str): The plain-text message to encrypt.
    Returns:
        str: The encrypted message.
    """
    ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    for letter in message:
        if letter.upper() in ABC:
            letter_index = (ABC.find(letter.upper()) + key) % len(ABC)
            encrypt_letter = ABC[letter_index]
            if letter.islower():
                encrypt_letter = encrypt_letter.lower()
            result += encrypt_letter
        else:
            result += letter
    return result

def cs_decrypt(key, message):
    """
    Decrypts a message encrypted with Caesar cipher using the given key.
    Parameters:
        key (int): The number of positions each letter was shifted.
        message (str): The encrypted message to decrypt.
    Returns:
        str: The decrypted message.
    """
    ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    for letter in message:
        if letter.upper() in ABC:
            letter_index = (ABC.find(letter.upper()) - key) % len(ABC)
            decrypted_letter = ABC[letter_index]
            if letter.islower():
                decrypted_letter = decrypted_letter.lower()
            result += decrypted_letter
        else:
            result += letter
    return result

def cs_cipher_brute_force(message):
    """
    Attempts to decrypt a Caesar cipher encrypted message using brute force.
    Parameters:
        message (str): The encrypted message to brute-force.
    Returns:
        str: The decrypted message if a valid English message is found.
    """
    with open('dictionary.txt', 'r') as f:
        words = f.readlines()

    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    print("Start brute force attack!!!")
    for k in range(1, len(alpha)):
        decrypted = cs_decrypt(k, message)
        if is_english.is_english_message(decrypted):
            print(f"key={k} -> {decrypted}")
            return decrypted
