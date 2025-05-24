from nltk.corpus import words
import os
import string


# abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
LETTERS = string.ascii_letters
LETTERS_AND_SPACE = LETTERS + ' \t\n'
# print(LETTERS_AND_SPACE)
DICTIONARY_FILE_PATH = "dictionary.txt"
ENGLISH_WORDS = set(words.words())

SUCCESS_PRECISION = 75


def load_dictionary():
    """
    load dictionary file and insert all words to set as lower case words
    :return: dictionary as set
    """
    dictionary_file = open(DICTIONARY_FILE_PATH)
    english_words = set()
    for word in dictionary_file.read().split('\n'):
        english_words.add(word.lower())
    dictionary_file.close()
    return english_words

# ENGLISH_WORDS = load_dictionary()

def load_message(file_name):
    """
    Load message content from text file
    :param file_name: text file path  + name
    :return: file content as string
    """
    in_file = f'files/{file_name}'
    if not os.path.exists(in_file):
        print(f"file {in_file} not exists")
        return ""
    with open(in_file, "r") as read_file:
        file_content = read_file.read()
    print(f"message loaded")
    return file_content


def remove_non_letters(message):
    """
    remove from message all punctuation signs
    :param message: message to manipulate
    :return: revised message
    """
    letters_only = []
    for symbol in message:
        if symbol in LETTERS_AND_SPACE:
            letters_only.append(symbol)
    return ''.join(letters_only)


def is_english_word(in_dictionary, word_to_check):
    """
    Check if word is in the dictionary
    :param in_dictionary:  set of words
    :param word_to_check: word to check
    :return: True if word in dictionary otherwise False
    """
    # Check if the word is in the dictionary
    if word_to_check.lower() in in_dictionary:
        print(f"pass - '{word_to_check}'")
        return True
    else:
        print(f"fail - '{word_to_check}'")
        return False


def count_english_words_and_check_precision(message):
    message = remove_non_letters(message)
    possible_words = message.split()
    # print(possible_words)
    if len(possible_words) == 0:
        return 0  # no words at all, so return 0
    unknown_words = []
    matches = 0
    for word in possible_words:
        if word.upper() in ENGLISH_WORDS or word.lower() in ENGLISH_WORDS:
            matches += 1
        else:
            unknown_words.append(word)
    total = len(possible_words)
    precision = float(matches) / total * 100
    return matches, total, round(precision, 2), unknown_words


def is_english_message(message, to_print=False):
    matches, total, precision, unknown_words = count_english_words_and_check_precision(message)
    if to_print:
        print(matches, total, precision, unknown_words)
    return precision >= SUCCESS_PRECISION