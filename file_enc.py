import base64
import cryptography
from cryptography.fernet import Fernet


def write_encrypted_file(contents, key, filename):
    key = key[:32]
    key = base64.urlsafe_b64encode(bytes(key, encoding='utf-8'))
    cipher = Fernet(key)
    enc_text = cipher.encrypt(contents.encode())
    with open(filename, 'wb') as file:
        file.write(enc_text)


def read_encrypted_file(filename, key):
    key = key[:32]
    key = base64.urlsafe_b64encode(bytes(key, encoding='utf-8'))
    cipher = Fernet(key)
    with open(filename, 'rb') as file:
        enc_text = file.read()
    plain_text = cipher.decrypt(enc_text).decode()
    return plain_text


def main():
    text = "Testing string."
    write_encrypted_file(text, '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4', 'enc.txt')
    with open('enc.txt', 'r') as file:
        print(file.read())
    read_text = read_encrypted_file('enc.txt', '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4')
    print(read_text)


if __name__ == '__main__':
    main()
