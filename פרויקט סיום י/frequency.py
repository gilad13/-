import os
from pydub.generators import Sine
from pydub import AudioSegment
from caesar import cs_encrypt, cs_decrypt
from is_english import is_english_message
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
special_chars = ' !"#$%&\'()*+,-./0123456789:;<=>?@[\\]^_`{|}~'

lenHalfAbc = 500
len2ndHalfAbc = 1000
lenSpecial = 250
lenBreak = 100
silent_wave = Sine(0).to_audio_segment(duration=lenBreak)

def text_to_audio(text, key):
    """
    Converts text into sound tones based on a key.
    Parameters:
    text (str): The text to convert.
    key (int): The key that changes the tone frequencies.
    Returns:
    AudioSegment: Audio made of sine wave tones representing the text.
    """
    audio = AudioSegment.silent(duration=0)
    for char in text:
        if char.isalpha():
            char = char.upper()
            index = alphabet.index(char)
            mod13 = index % 13
            freq = (mod13 * 100 * key) + 400
            duration = lenHalfAbc if index < 13 else len2ndHalfAbc
        elif char in special_chars:
            index = special_chars.index(char)
            freq = 2000 + index * 50  # fixed tone for special characters
            duration = lenSpecial
        else:
            continue
        audio += Sine(freq).to_audio_segment(duration=duration) + silent_wave
    return audio

def save_audio(audio, filename):
    """
    Saves audio data to a WAV file.
    Parameters:
    audio (AudioSegment): The audio to save.
    filename (str): The name of the file to save to.
    Returns:
    None
    """
    audio.export(filename, format="wav")

def get_frequencies(filename, window_size_ms=50):
    """
    Reads audio file and finds main frequency in small time windows.
    Parameters:
    filename (str): Audio file path.
    window_size_ms (int): Size of time window in milliseconds (default 50ms).
    Returns:
    list of float: List of main frequencies found in each window.
    """
    sr, audio = wavfile.read(filename)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    win_size = int(window_size_ms / 1000 * sr)
    f, _, Zxx = stft(audio, fs=sr, nperseg=win_size, noverlap=0)
    return [f[np.argmax(np.abs(Zxx[:, i]))] for i in range(Zxx.shape[1])]

def freq_list_to_time_freq(filename):
    """
    Turns frequency list into pairs of frequency and duration by detecting silence.
    Parameters:
    filename (str): Audio file path.
    Returns:
    list of [float, int]: List of [frequency, duration] pairs.
    """
    freqs = get_frequencies(filename)
    result = []
    count = 0
    for i, freq in enumerate(freqs):
        count += 1
        if freq == 0 and i < len(freqs) - 1:
            result.append([freqs[i - 1], count - 2])
            count = 0
    return result

def list_to_letters(filename, key):
    """
    Converts frequency and duration pairs back to text using the key.
    Parameters:
    filename (str): Audio file path.
    key (int): The key used to decode.
    Returns:
    str: The decoded text.
    """
    freq_time = freq_list_to_time_freq(filename)
    decrypted = ""
    for freq, time in freq_time:
        mod13 = int(((freq - 400) / (100 * key)) % 13)
        if time == 10:  # Letters A-M
            for i in range(13):
                if i % 13 == mod13:
                    decrypted += alphabet[i]
                    break
        elif time == 20:  # Letters N-Z
            for i in range(13, 26):
                if i % 13 == mod13:
                    decrypted += alphabet[i]
                    break
        elif time == 5:  # Special characters
            index = int(round((freq - 2000) / 50))
            if 0 <= index < len(special_chars):
                decrypted += special_chars[index]
    return decrypted

def validate_params_decrypt(filename, key):
    """
    Checks if decryption inputs are valid.
    Parameters:
    filename (str): Audio file name.
    key (int): Decryption key.
    Returns:
    bool: True if valid, False if invalid.
    """
    if not isinstance(key, int) or key < 0 or key > 13:
        print(f"[Error] Key '{key}' must be an integer between 0 and 13.")
        return False
    if not isinstance(filename, str) or not filename.strip():
        print("[Error] Filename must be a non-empty string.")
        return False
    valid_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
    ext = os.path.splitext(filename)[1].lower()
    if ext not in valid_extensions:
        print(f"[Error] Filename must end with one of {valid_extensions}.")
        return False
    return True

def validate_params_encrypt(text, key, filename):
    """
    Checks if encryption inputs are valid.
    Parameters:
    text (str): Text to encrypt.
    key (int): Encryption key.
    filename (str): Output filename.
    Returns:
    bool: True if valid, False if invalid.
    """
    all_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ !#$%&\'()*+,-./0123456789:;<=>?@[\\]^_`{|}~"
    if not validate_params_decrypt(filename, key):
        return False
    if not isinstance(text, str):
        print("Text must be a string.")
        return False
    for i in text:
        if i.upper() not in all_characters:
            return False, "Text can only contain this characters: ABCDEFGHIJKLMNOPQRSTUVWXYZ !#$%&\'()*+,-./0123456789:;<=>?@[\\]^_`{|}~"
    return True

def encrypt(text, key, filename):
    """
    Encrypts text with Caesar cipher, converts it to audio, and saves to file.
    Parameters:
    text (str): Text to encrypt.
    key (int): Encryption key.
    filename (str): Output file name.
    Returns:
    False if parameters invalid, else None.
    """
    if not validate_params_encrypt(text, key, filename):
        return False
    enc_text = cs_encrypt(key, text)
    audio = text_to_audio(enc_text, key)
    save_audio(audio, filename)

def decrypt(key, filename):
    """
    Reads an audio file and decrypts the message inside.
    Parameters:
    key (int): Decryption key.
    filename (str): Audio file name.
    Returns:
    str: Decrypted message, or False if input invalid.
    """
    if not validate_params_decrypt(filename, key):
        return False
    enc_text = list_to_letters(filename, key)
    return cs_decrypt(key, enc_text)

def hack(filename):
    """
    Tries all possible keys (1 to 9) to decrypt the audio until English text is found.
    Parameters:
    filename (str): Audio file name.
    Returns:
    str: Decrypted message and key if found, else error message.
    """
    for key in range(1, 14):
        msg = decrypt(key, filename)
        if is_english_message(msg):
            return f"decrypted message: {msg} optional key: {key}"
    return "no valid key found"


def validate_frequency_decrypt_inputs(audio_file, key):
    """
    Validates inputs for frequency-based decryption.
    Parameters:
    audio_file (str): Path to audio file.
    key (any): Decryption key.
    Returns:
    tuple(bool, str/int): (True, key_int) if valid; (False, error_message) otherwise.
    """
    if audio_file is None:
        return False, "No audio file provided."
    if not os.path.isfile(audio_file):
        return False, "Invalid file path."
    try:
        key_int = int(key)
    except:
        return False, "Key must be an integer."
    if not (0 <= key_int <= 13):
        return False, "Key must be between 0 and 13."
    ext = os.path.splitext(audio_file)[1].lower()
    if ext not in ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']:
        return False, f"File extension {ext} not supported."
    return True, key_int

def validate_frequency_encrypt_inputs(text, key):
    """
    Validates inputs for frequency-based encryption.
    Parameters:
    text (str): Text to encrypt.
    key (any): Encryption key.
    Returns:
    tuple(bool, str/int): (True, key_int) if valid; (False, error_message) otherwise.
    """
    if not text or not isinstance(text, str):
        return False, "Text must be a non-empty string."
    try:
        key_int = int(key)
    except:
        return False, "Key must be an integer."
    if not (0 <= key_int <= 13):
        return False, "Key must be between 0 and 13."
    return True, key_int

def validate_frequency_hack_inputs(audio_file):
    """
    Validates inputs for frequency-based hacking (brute-force decryption).
    Parameters:
    audio_file (str): Path to audio file.
    Returns: tuple(bool, str/None): (True, None) if valid; (False, error_message) otherwise.
    """
    if audio_file is None:
        return False, "No audio file provided."
    if not os.path.isfile(audio_file):
        return False, "Invalid file path."
    ext = os.path.splitext(audio_file)[1].lower()
    if ext not in ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']:
        return False, f"File extension {ext} not supported."
    return True, None


def check_code_functionality():
    """
    Tests the encryption and decryption process.
    Steps:
    - Encrypts a sample text and saves it to a file.
    - Decrypts the saved file and compares to original.
    - Attempts to crack the encryption using brute force.
    Prints results to the console.
    """
    text = "HELLO, how Are you Today? I am fine, thank you. Goodbye!!!"
    key = 4
    filename = "encrypted.wav"

    if encrypt(text, key, filename) != False:
        encrypt(text, key, filename)
        print("[+] Audio saved.")
    decrypted = decrypt(key, filename)
    if decrypted != False:
        print("[+] Decrypted:", decrypted)
        print("[✓] Match:" if decrypted.upper() == text.upper() else "[✗] Mismatch")
    hacked = hack(filename)
    print("[?] Brute-force result:", hacked)


if __name__ == '__main__':
    check_code_functionality()