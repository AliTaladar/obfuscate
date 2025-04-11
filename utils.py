import random
import string

def generate_obscure_name():
    """Generate a random, obscure name starting with a letter followed by 7 alphanumeric chars."""
    letters = string.ascii_letters
    digits = string.digits
    return random.choice(letters) + ''.join(random.choices(letters + digits, k=7))

def encode(s):
    """Encode a string by shifting each character's ASCII value up by 1."""
    return ''.join(chr(ord(c) + 1) for c in s)