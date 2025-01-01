from cryptography.fernet import Fernet

# Load the encryption key
with open("secret.key", "rb") as key_file:
    key = key_file.read()

# Initialize the cipher
cipher = Fernet(key)

# Tokens to encrypt
mantis_token = ""
gitlab_token = ""

# Encrypt the tokens
encrypted_mantis_token = cipher.encrypt(mantis_token.encode())
encrypted_gitlab_token = cipher.encrypt(gitlab_token.encode())

# Save the encrypted tokens to a file
with open("encrypted_tokens.txt", "wb") as token_file:
    token_file.write(encrypted_mantis_token + b"\n" + encrypted_gitlab_token)

print("Tokens encrypted and saved to 'encrypted_tokens.txt'.")
