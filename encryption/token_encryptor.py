from cryptography.fernet import Fernet

token_file_txt="encrypted_tokens_ps.txt"

# Load the encryption key
with open("secret.key", "rb") as key_file:
    key = key_file.read()

# Initialize the cipher
cipher = Fernet(key)

# Tokens to encrypt
mantis_token = "8kLhQyA-e-q6Na4j5UBsyEdYckARlzB_"
gitlab_token = "EM9n2Dpu8e5KyA1gyVDK"

# Encrypt the tokens
encrypted_mantis_token = cipher.encrypt(mantis_token.encode())
encrypted_gitlab_token = cipher.encrypt(gitlab_token.encode())

# Save the encrypted tokens to a file
with open(token_file_txt, "wb") as token_file:
    token_file.write(encrypted_mantis_token + b"\n" + encrypted_gitlab_token)

print(f"Tokens encrypted and saved to '{token_file_txt}'.")
