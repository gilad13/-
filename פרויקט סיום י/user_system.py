import json
import os
import hashlib

USERS_FILE = "users.json"
LOGS_FILE = "logs.json"

def _load_data(filename):
    """
    Loads JSON data from a file.
    Parameters:
        filename (str): The name of the file to load data from.
    Returns:
        dict: The data loaded from the file or an empty dictionary if the file does not exist.
    """
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        return json.load(f)

def _save_data(filename, data):
    """
    Saves a dictionary as JSON to a file.
    Parameters:
        filename (str): The name of the file to save the data to.
        data (dict): The data to be saved.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def _hash_password(password):
    """
    Hashes a password using SHA-256.
    Parameters:
        password (str): The plain-text password to hash.
    Returns:
        str: The SHA-256 hash of the password in hexadecimal.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """
    Registers a new user with a hashed password.
    Parameters:
        username (str): The username to register.
        password (str): The plain-text password to associate with the user.
    Returns:
        tuple: (bool, str) indicating success status and a message.
    """
    users = _load_data(USERS_FILE)
    if username in users:
        return False, "Username already exists"
    users[username] = _hash_password(password)
    _save_data(USERS_FILE, users)
    return True, "User registered successfully"

def login_user(username, password):
    """
    Logs in a user by verifying the hashed password.
    Parameters:
        username (str): The username to log in.
        password (str): The plain-text password to verify.
    Returns:
        tuple: (bool, str, str or None) indicating success, message, and the username if successful.
    """
    users = _load_data(USERS_FILE)
    hashed = _hash_password(password)
    if username not in users:
        return False, "Username does not exist", None
    if users[username] != hashed:
        return False, "Incorrect password", None
    return True, "Login successful", username