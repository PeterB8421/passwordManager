import base64
import csv
import io
import os
import cryptography
from cryptography.fernet import Fernet


def write_encrypted_file(contents, key: bytes, filename):
    """
    Encypts contents and writes them to a file.
    :param contents: Text to be encrypted and written.
    :param key: Key used for encryption.
    :param filename: Name of a file to write to.
    :return:
    """
    key = key[:32]
    key = base64.urlsafe_b64encode(key)
    cipher = Fernet(key)
    enc_text = cipher.encrypt(contents.encode())
    with open(filename, 'wb') as file:
        file.write(enc_text)


def read_encrypted_file(filename, key: bytes):
    """
    Reads an encrypted file, decrypts it and returns it.
    :param filename: Name of a file to read.
    :param key: Key for decryption.
    :return: Decrypted file content in string.
    """
    key = key[:32]
    key = base64.urlsafe_b64encode(key)
    cipher = Fernet(key)
    with open(filename, 'rb') as file:
        enc_text = file.read()
    plain_text = cipher.decrypt(enc_text.strip()).decode()
    return plain_text


def write_to_csv(content, filename, header, key):
    """
    Writes content into a csv file and encrypts it.
    :param content: Data to be written into file.
    :param filename: Name of file to write into.
    :param header: CSV header as list.
    :param key: Encryption key to be used.
    :return:
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=header)
    writer.writeheader()
    writer.writerows(content)

    raw_data = output.getvalue()
    write_encrypted_file(raw_data, key, filename)


def read_from_csv(filename, key):
    """
    Reads data from csv file and decrypts it.
    :param filename: Name of the CSV file.
    :param key: Encryption key to be used.
    :return: Dict of CSV data.
    """
    if not os.path.exists(filename):
        return []
    raw_data = read_encrypted_file(filename, key)
    csv_file = io.StringIO(raw_data)
    csv_dict = list(csv.DictReader(csv_file))
    csv_file.close()
    return csv_dict


def main():
    # text = "Testing string."
    # write_encrypted_file(text, '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4', 'enc.txt')
    # with open('enc.txt', 'r') as file:
    #     print(file.read())
    # read_text = read_encrypted_file('enc.txt', '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4')
    # print(read_text)
    salts = [
        {'id': 1, 'salt': 'utyasfdguytgf'},
        {'id': 2, 'salt': 'iuwaeghyrfbn'},
    ]
    write_to_csv(salts, 'data/salts.csv', ['id', 'salt'])
    read_data = read_from_csv('data/salts.csv')
    print(read_data)


if __name__ == '__main__':
    main()
