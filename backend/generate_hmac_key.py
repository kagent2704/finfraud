# generate_hmac_key.py
import secrets

# Generate 32 random bytes and convert to hex
key = secrets.token_hex(32)
print("Your new LEDGER_HMAC_KEY is:\n", key)
