from Crypto.Random import get_random_bytes
print(get_random_bytes(32)) # Print the salt to be copied to your script

from Crypto.Cipher import AES

data = b'abcdefghijklmnopqrstuvwzyz'

key = b'Sixteen byte key'
cipher = AES.new(key, AES.MODE_OCB)

nonce = cipher.nonce
ciphertext, tag = cipher.encrypt_and_digest(data)