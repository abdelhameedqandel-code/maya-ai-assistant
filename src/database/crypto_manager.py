import os
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()


class VaultCryptoManager:
    """
    Handles symmetric AES-based encryption and decryption (Fernet)
    for sensitive user notes, daily logs, and secrets stored locally.
    """

    def __init__(self, master_key: str | None = None):
        key = master_key or os.getenv("VAULT_MASTER_KEY")
        if not key:
            raise ValueError(
                "VAULT_MASTER_KEY is missing. Generate one using "
                "`VaultCryptoManager.generate_key()` and store it in your `.env` file."
            )
        self.cipher = Fernet(key.encode("utf-8"))

    @staticmethod
    def generate_key() -> str:
        """Generates a cryptographically secure 32-byte URL-safe base64 key."""
        return Fernet.generate_key().decode("utf-8")

    def encrypt(self, plain_text: str) -> str:
        """Encrypts a UTF-8 string and returns a base64-encoded ciphertext string."""
        if not plain_text:
            return ""
        encrypted_bytes = self.cipher.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        """Decrypts a ciphertext string back to its original UTF-8 text."""
        if not cipher_text:
            return ""
        try:
            decrypted_bytes = self.cipher.decrypt(cipher_text.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken as exc:
            raise PermissionError(
                "Decryption failed: Invalid VAULT_MASTER_KEY or corrupted vault data."
            ) from exc


if __name__ == "__main__":
    # Quick local test & key generator
    sample_key = VaultCryptoManager.generate_key()
    print(f"Generated Master Key (Save this in .env):\nVAULT_MASTER_KEY={sample_key}\n")

    manager = VaultCryptoManager(master_key=sample_key)
    secret = "موعد تسليم مشروع التخرج يوم الأحد الساعة 10 صباحاً"
    encrypted = manager.encrypt(secret)
    decrypted = manager.decrypt(encrypted)

    print(f"Original : {secret}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")