import gradio as gr
from frequency import encrypt as freq_encrypt, decrypt as freq_decrypt, hack as freq_hack
from pyramid import encrypt_pyramid, decrypt_pyramid, hack_pyramid, checking_parameters
from user_system import register_user, login_user
import os


# --- פונקציות ---

def do_register(username, password):
    """
    Registers a new user in the system with given username and password.
    username: The username for the new user to register.
    password: The password for the new user to register.
    return: A string message indicating whether registration was successful or if the username already exists.
    """
    # בדיקת קלטים לפני ניסיון רישום
    if not username or not username.strip():
        return "Username is required. Please enter a username."

    if not password or not password.strip():
        return "Password is required. Please enter a password."

    if len(username.strip()) < 3:
        return "Username must be at least 3 characters long."

    if len(password.strip()) < 4:
        return "Password must be at least 4 characters long."

    # אם הקלטים תקינים, נסה לרשום
    success, msg = register_user(username.strip(), password.strip())
    return msg


def do_login(username, password, user_state):
    """
    Attempts to login a user with given username and password.
    username: The username to login.
    password: The password to login.
    user_state: The current user state (ignored here but required by interface).
    return: Tuple (message string, user data or None) depending on login success.
    """
    # בדיקת קלטים לפני ניסיון התחברות
    if not username or not username.strip():
        return "Username is required. Please enter a username.", None

    if not password or not password.strip():
        return "Password is required. Please enter a password.", None

    # אם הקלטים תקינים, נסה להתחבר
    success, msg, user = login_user(username.strip(), password.strip())
    if success:
        return msg, user
    else:
        return msg, None


# בדיקת קלטים להצפנה בשיטת Frequency
def validate_frequency_encrypt_inputs(text, key):
    """
    Validates inputs for Frequency encryption.
    text: The text to encrypt, must be a non-empty string.
    key: The encryption key, expected to be convertible to integer between 0 and 13.
    return: Tuple (bool valid, int key or error message string)
    """
    all_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ !#$%&\'()*+,-./0123456789:;<=>?@[\\]^_`{|}~"
    if not text or not isinstance(text, str):
        return False, "Text must be a non-empty string."
    try:
        key_int = int(key)
    except:
        return False, "Key must be an integer."
    if not (0 <= key_int <= 13):
        return False, "Key must be between 0 and 13."
    for i in text:
        if i.upper() not in all_characters:
            return False, "Text can only contain this characters: ABCDEFGHIJKLMNOPQRSTUVWXYZ !#$%&\'()*+,-./0123456789:;<=>?@[\\]^_`{|}~"
    return True, key_int


def freq_encrypt_gui(text, key, user_state):
    """
    Encrypts text into audio using Frequency method, if user is logged in.
    text: Text string to encrypt.
    key: Integer key for encryption.
    user_state: Current logged-in user or None.
    return: Tuple (status message string, path to encrypted audio file or None).
    """
    if not user_state:
        return "Please login first.", None
    valid, result = validate_frequency_encrypt_inputs(text, key)
    if not valid:
        return result, None
    key_int = result

    output_path = "encrypted_audio.wav"
    try:
        freq_encrypt(text, key_int, output_path)
        return "Encryption successful.", output_path
    except Exception as e:
        return f"Encryption failed: {e}", None


# בדיקת קלטים לפענוח בשיטת Frequency
def validate_frequency_decrypt_inputs(audio_file, key):
    """
    Validates inputs for Frequency decryption.
    audio_file: Path to audio file, must exist and be a supported audio format.
    key: Key to decrypt, must be integer between 0 and 13.
    return: Tuple (bool valid, int key or error message string)
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


def freq_decrypt_gui(audio_file, key, user_state):
    """
    Decrypts audio file encrypted with Frequency method using the provided key.
    audio_file: Path to the audio file to decrypt.
    key: Integer key used for decryption.
    user_state: Current logged-in user or None.
    return: Decrypted text string or error message.
    """
    if not user_state:
        return "Please login first."
    valid, result = validate_frequency_decrypt_inputs(audio_file, key)
    if not valid:
        return result
    key_int = result
    try:
        decrypted_text = freq_decrypt(key_int, audio_file)
        return decrypted_text
    except Exception as e:
        return f"Decryption failed: {e}"


def validate_frequency_hack_inputs(audio_file):
    """
    Validates input audio file for Frequency hack (no key).
    audio_file: Path to audio file, must exist and be supported format.
    return: Tuple (bool valid, error message string or None)
    """
    if audio_file is None:
        return False, "No audio file provided."
    if not os.path.isfile(audio_file):
        return False, "Invalid file path."
    ext = os.path.splitext(audio_file)[1].lower()
    if ext not in ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']:
        return False, f"File extension {ext} not supported."
    return True, None


def freq_hack_gui(audio_file, user_state):
    """
    Attempts to hack Frequency encrypted audio without knowing the key.
    audio_file: Path to encrypted audio file.
    user_state: Current logged-in user or None.
    return: Result string of hacked text or error message.
    """
    if not user_state:
        return "Please login first."

    valid, error_msg = validate_frequency_hack_inputs(audio_file)
    if not valid:
        return error_msg

    try:
        result = freq_hack(audio_file)
        return result
    except Exception as e:
        return f"Hack failed: {str(e)}"


def pyramid_encrypt_gui(text, key, user_state):
    """
    Encrypts text using the Pyramid method with a numeric key.
    text: The plaintext message to encrypt.
    key: Numeric key as integer, shorter than 7 digits and containing all digits from 1 to key length.
    user_state: Current logged-in user or None.
    return: Encrypted text or error message string.
    """
    if not user_state:
        return "Please login first."
    try:
        key_int = int(key)
    except ValueError:
        return "Key must be an integer."
    valid, message = checking_parameters(text, key_int)
    if not valid:
        return message
    if encrypt_pyramid(text, key_int)[1] == "text can not contain $ sign":
        return encrypt_pyramid(text, key_int)[1]
    return encrypt_pyramid(text, key_int)


def pyramid_decrypt_gui(ciphertext, key, user_state):
    """
    Decrypts text encrypted with Pyramid method using the provided key.
    ciphertext: The encrypted text to decrypt.
    key: Numeric key as integer, same rules as for encryption.
    user_state: Current logged-in user or None.
    return: Decrypted original text or error message string.
    """
    if not user_state:
        return "Please login first."

    try:
        key_int = int(key)
    except ValueError:
        return "Key must be an integer."

    valid, message = checking_parameters(ciphertext, key_int)
    if not valid:
        return message

    return decrypt_pyramid(ciphertext, key_int)


def pyramid_hack_gui(ciphertext, user_state):
    """
    Attempts to hack the Pyramid encrypted text without a key.
    ciphertext: The encrypted text to hack.
    user_state: Current logged-in user or None.
    return: Hacked text or error message string.
    """
    if not user_state:
        return "Please login first."
    return hack_pyramid(ciphertext)


with gr.Blocks() as app:
    user_state = gr.State(value=None)

    with gr.Tab("Login/Register"):
        gr.Markdown("### Please login or register")
        with gr.Row():
            login_username = gr.Textbox(label="Username")
            login_password = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_status = gr.Textbox(label="Status", interactive=False)

        with gr.Row():
            register_username = gr.Textbox(label="New Username")
            register_password = gr.Textbox(label="New Password", type="password")
        register_button = gr.Button("Register")
        register_status = gr.Textbox(label="Status", interactive=False)

        login_button.click(do_login, [login_username, login_password, user_state], [login_status, user_state])
        register_button.click(do_register, [register_username, register_password], register_status)

    with gr.Tab("Encrypt/Decrypt Frequency"):
        gr.Markdown("""
        ### Frequency Method

        #### Frequency Encryption  
        In this encryption method, you provide a text and a key (integer between 0 and 13).  
        The duration of each character's sound is determined as follows:
        - Letter from the first 13 letters of the alphabet: 0.5 seconds  
        - Letter from the last 13 letters of the alphabet: 1 second  
        - Special character: 0.25 seconds  
        - Pause of 0.1 seconds between each character

        The frequency for each character is calculated as:

        **For letters A–Z:**  
        `(((position_in_alphabet + key) % 13) * 100 * key) + 400`

        **For special characters:**  
        `((position_in_special_chars) * 50) + 2000`

        The frequencies and durations are converted into a sound file using `pydub` and `pydub.generators`, specifically `AudioSegment` and the `Sine` generator.

        ---

        #### Frequency Decryption  
        Provide the audio file and the key.  
        The audio is analyzed into frequencies and durations using:
        - `scipy.io.wavfile`
        - `scipy.signal.stft`
        - `numpy`

        **Position calculation:**  
        - For durations 0.5 or 1 second:
          `(100 * key) / (freq - 400) % 13`  
          - 0.5 seconds → position in first 13 letters  
          - 1 second → position + 13  
          Then apply Caesar decryption backwards using the key.

        - For special characters (0.25 seconds):
          `(freq - 2000) / 50`

        > The final decrypted message is always displayed in **uppercase** letters.

        ---

        #### Frequency Hack  
        The **Frequency Hack** function is used when the key to decrypt a frequency-based audio file is unknown.  
        It works by trying all possible keys from **0 to 13**.

        For each key, the function attempts to decrypt the audio file and checks whether the resulting message is valid **English**.  
        The first valid result is returned along with the key that was used.

        > The decrypted message is always displayed in **uppercase** letters.

        If no English message is found after all key attempts, it returns a message stating that no valid key was found.

        This function is useful for recovering the original message without knowing the encryption key.

        """)

        freq_text = gr.Textbox(label="Text to encrypt")
        freq_key = gr.Textbox(label="Key (integer)")
        freq_encrypt_btn = gr.Button("Encrypt")
        freq_encrypt_status = gr.Textbox(label="Status", interactive=False)
        freq_encrypt_file = gr.File(label="Download Encrypted Audio")

        freq_audio_file = gr.File(label="Audio file to decrypt or hack",
                                  file_types=['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'], type="filepath")
        freq_key_decrypt = gr.Textbox(label="Key (integer) for decryption")
        freq_decrypt_btn = gr.Button("Decrypt")
        freq_decrypt_output = gr.Textbox(label="Decrypted Text")

        freq_hack_btn = gr.Button("Hack (No Key Needed)")
        freq_hack_output = gr.Textbox(label="Hacked Text")

        freq_encrypt_btn.click(
            fn=freq_encrypt_gui,
            inputs=[freq_text, freq_key, user_state],
            outputs=[freq_encrypt_status, freq_encrypt_file]
        )
        freq_decrypt_btn.click(
            fn=freq_decrypt_gui,
            inputs=[freq_audio_file, freq_key_decrypt, user_state],
            outputs=freq_decrypt_output
        )
        freq_hack_btn.click(
            fn=freq_hack_gui,
            inputs=[freq_audio_file, user_state],
            outputs=freq_hack_output
        )

    with gr.Tab("Encrypt/Decrypt Pyramid"):
        gr.Markdown("""
    ### Pyramid Method

    #### Pyramid Encryption  
    In this method, a **text message** and a **numeric key** are provided.  
    The key must be **shorter than 8 digits** and must contain **all digits from 1 to the length of the key** in any order.  
    For example: `3124`, `263415`.

    The digits in the key are **mirrored**, key reversed in index values.  
    Example: for key `3124`, the mirrored key is `4213`.

    The message is written **column by column** into a 2D grid with a number of columns equal to the length of the key.

    Example:  
    Message: `hello world how are you?`  
    Key: `3124` → Mirrored: `4213`

    Grid filled (column by column):

    | 1 | 2 | 3 | 4 |
    |---|---|---|---|
    | h |   |   |   |
    | e | l |   |   |
    | l | o |   |   |
    | w | o | r | l |
    | d |   |   |   |
    | h | o |   |   |
    | w |   | a |   |
    | r | e |   | y |
    | o |   |   |   |
    | u | ? |   |   |

    **Empty cells are represented as `$`**.

    The encrypted message is read **by columns**, in the order defined by the mirrored key.  
    So for key `3124` → read columns 4, 2, 1, then 3.

    ---

    #### Pyramid Decryption  
    The decryption process also requires the same key.  
    The encrypted message is first placed **into columns** according to the mirrored key:
    | 4 | 2 | 1 | 3 |
    |---|---|---|---|
    | $ | $ | h | $ |
    | $ | l | e | $ |
    | $ | o | l |   |
    | l | o | w | r |
    | $ | $ | d | $ |
    | $ | h |   | $ |
    | $ | w | o |   |
    |   | r | a | e |
    | $ | $ | y | $ |
    | $ | u | o | $ |
    | $ | $ | ? | $ |

    then **reordered** back to their original column order 1-key length.

    Finally, the message is **read row by row**, and all `$` placeholders are removed to get the original text.

    ---

    #### Pyramid Hack  
    The **Pyramid Hack** function is used when the key to decrypt a pyramid-encrypted message is unknown.  
    It works by trying all valid key permutations for key lengths from **2 to 7**.

    For each key length, it generates all possible valid keys — each being a permutation of digits from 1 to the key length.  
    It then tries to decrypt the message with each key and checks whether the result is **valid English**.

    If a readable message is found, it returns the **decrypted message** along with the **key used**.

    If no valid message is found, it returns a message indicating that no possible key was found.

    This method is useful when you only have the encrypted message but not the key used for pyramid encryption.

    ---

    """)
        pyramid_text = gr.Textbox(label="Text to encrypt/decrypt")
        pyramid_key = gr.Textbox(label="Key (integer)")
        pyramid_encrypt_btn = gr.Button("Encrypt")
        pyramid_encrypt_output = gr.Textbox(label="Encrypted Text")

        pyramid_decrypt_btn = gr.Button("Decrypt (fill the text in 'Text to encrypt/decrypt')")
        pyramid_decrypt_output = gr.Textbox(label="Decrypted Text")

        pyramid_hack_btn = gr.Button("Hack (fill the text in 'Text to encrypt/decrypt', no key is needed)")
        pyramid_hack_output = gr.Textbox(label="Hacked Text")

        pyramid_encrypt_btn.click(pyramid_encrypt_gui, [pyramid_text, pyramid_key, user_state], pyramid_encrypt_output)
        pyramid_decrypt_btn.click(pyramid_decrypt_gui, [pyramid_text, pyramid_key, user_state], pyramid_decrypt_output)
        pyramid_hack_btn.click(pyramid_hack_gui, [pyramid_text, user_state], pyramid_hack_output)

app.launch(share=True)
