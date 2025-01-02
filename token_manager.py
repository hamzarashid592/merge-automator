from cryptography.fernet import Fernet
from config_manager import ConfigurationManager

# Initialize the configuration manager
config = ConfigurationManager()

class TokenManager:
    def __init__(self, key_file=config.get("KEY_FILE"), token_file=config.get("TOKEN_FILE")):
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
