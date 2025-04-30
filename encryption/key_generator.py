from cryptography.fernet import Fernet

# Generate an encryption key
key = Fernet.generate_key()

# Save the key to a file
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Encryption key saved to 'secret.key'.")
