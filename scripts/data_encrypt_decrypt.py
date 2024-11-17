from cryptography.fernet import Fernet
from navyojan import settings

key = settings.FERNET_KEY.encode()

# Create a Fernet instance with the key
cipher = Fernet(key)

def encrypt_data(data: str) -> str:
    """Encrypts the given string data."""
    if not isinstance(data, bytes):
        data = data.encode()  # Convert string to bytes
    encrypted_data = cipher.encrypt(data)
    return encrypted_data.decode()  # Return as a string for easier storage

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts the given encrypted string data."""
    decrypted_data = cipher.decrypt(encrypted_data.encode())  # Convert string to bytes
    return decrypted_data.decode()