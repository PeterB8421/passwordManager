import base64
import csv
import io
import os
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


def write_to_csv(content, filename, header):
    """
    Writes content into a csv file and encrypts it.
    :param content: Data to be written into file.
    :param filename: Name of file to write into.
    :param header: CSV header as list.
    :return:
    """
    with open(filename, 'w', newline="", encoding='utf-8') as file:
        csv_writer = csv.DictWriter(file, header)
        csv_writer.writeheader()
        csv_writer.writerows(content)

    raw_data = ""
    with open(filename, 'r', newline="", encoding='utf-8') as file:
        raw_data = file.read()
    write_encrypted_file(raw_data, '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4', filename)


def read_from_csv(filename):
    """
    Reads data from csv file and decrypts it.
    :param filename: Name of the CSV file.
    :return: Dict of CSV data.
    """
    if not os.path.exists(filename):
        return []
    raw_data = read_encrypted_file(filename, '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4')
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
