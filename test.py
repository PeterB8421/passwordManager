import csv
import getpass
import io
import os.path
import sys

from argon2.low_level import hash_secret_raw, Type
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import hashlib
from base64 import b64encode, b64decode

import file_enc
from db_test import DbManager
from master_pass_db import MasterPassManager


MASTER_PASSWORD_HASH = '$argon2id$v=19$m=65536,t=3,p=4$RXs4DyzttrUtklEinbfeWA$VxGKk4nmUoR9Hw63tsfCI68liFUgNjb79eh7horE9+4'


def encrypt(plain_text, key):
    salt = get_random_bytes(AES.block_size)
    pk = hashlib.scrypt(key.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

    cipher_config = AES.new(pk, AES.MODE_GCM)
    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
    return {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'salt'       : b64encode(salt).decode('utf-8'),
        'nonce'      : b64encode(cipher_config.nonce).decode('utf-8'),
        'tag'        : b64encode(tag).decode('utf-8')
    }


def decrypt(enc_dict, key):
    salt = b64decode(enc_dict['salt'])
    cipher_text = b64decode(enc_dict['cipher_text'])
    nonce = b64decode(enc_dict['nonce'])
    tag = b64decode(enc_dict['tag'])

    pk = hashlib.scrypt(key.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    cipher = AES.new(pk, AES.MODE_GCM, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(cipher_text, tag)
    return decrypted


def add_pass():
    password = getpass.getpass('Enter password to save: ')
    enc_password = encrypt(password, MASTER_PASSWORD_HASH)
    db = DbManager()
    db.insert('test', password=enc_password['cipher_text'], salt=enc_password['salt'],
              nonce=enc_password['nonce'], tag=enc_password['tag'], url='https://example.com')
    print('Password saved!')


def get_pass():
    url = input("Enter URL: ")
    db = DbManager()
    results = db.get_by_url(url)
    print('ID, URL, username, note\n')
    for res in results:
        print(f'{res[0]}, {res[1], res[2], res[3]}\n')
    choice = 0
    while True:
        try:
            choice = int(input('Enter ID: '))
            break
        except ValueError:
            print('Enter a number!', file=sys.stderr)
    row = db.get_by_id(choice)
    if row is None:
        print('Invalid ID!', file=sys.stderr)
        return
    salts = file_enc.read_encrypted_file('data/salts.csv', MASTER_PASSWORD_HASH)
    temp = io.StringIO(salts)
    reader = csv.DictReader(temp)
    salts_dict = [row for row in reader]
    salt_row = None
    for r in salts_dict:
        if int(r['id']) == choice:
            salt_row = r
            break
    if salt_row is None:
        print('Error reading salts!', file=sys.stderr)
        exit(1)
    # print(row[3], salt_row['salt'], salt_row['nonce'], salt_row['tag'])
    enc_dict = {
        'cipher_text': row[3],
        'salt': salt_row['salt'],
        'nonce': salt_row['nonce'],
        'tag': salt_row['tag']
    }
    print(decrypt(enc_dict, MASTER_PASSWORD_HASH))


def main():
    choice = 0
    while True:
        try:
            choice = int(input("1 Add a password\n"
                               "2 Get a password\n"))
            if choice in [1, 2]:
                break
            else:
                print("Invalid choice!", file=sys.stderr)
        except ValueError:
            print("You did not enter a number!", file=sys.stderr)

    match choice:
        case 1:
            add_pass()
        case 2:
            get_pass()
        case 0:
            print("Invalid option!", file=sys.stderr)
            return 1


def hash_master_pass(password: bytes, salt):
    time_cost = 3
    memory_cost = 65536
    parallelism = 4
    hash_len = 32

    derived_hash = hash_secret_raw(
        secret=password,
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=hash_len,
        type=Type.ID
    )
    return derived_hash


def pass_hash_test():
    mpass_manager = MasterPassManager()
    if not mpass_manager.is_set():
        mpass_manager.set_master_salt()
    master_password = getpass.getpass('Enter master password: ')
    salt = mpass_manager.get_salt()
    master_hash = hash_master_pass(master_password.encode('utf-8'), salt)
    print(b64encode(master_hash))


if __name__ == '__main__':
    pass_hash_test()
    # main()
