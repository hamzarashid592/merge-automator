from cryptography.fernet import Fernet

class TokenManager:
    def __init__(self, key_file, token_file):
        # Load the encryption key
        with open(key_file, "rb") as kf:
            self.key = kf.read()
        self.cipher = Fernet(self.key)
        self.token_file = token_file

    def get_tokens(self):
        """
        Decrypt and return the tokens as a dictionary.
        """
        with open(self.token_file, "rb") as tf:
            encrypted_tokens = tf.readlines()
        
        return {
            "mantis_token": self.cipher.decrypt(encrypted_tokens[0].strip()).decode(),
            "gitlab_token": self.cipher.decrypt(encrypted_tokens[1].strip()).decode(),
        }

    def save_tokens(self, mantis_token, gitlab_token):
        """
        Encrypt and save tokens to the token file.
        """
        encrypted_mantis = self.cipher.encrypt(mantis_token.encode())
        encrypted_gitlab = self.cipher.encrypt(gitlab_token.encode())

        with open(self.token_file, "wb") as tf:
            tf.write(encrypted_mantis + b"\n" + encrypted_gitlab)
