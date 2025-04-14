import csv
import getpass
import io
import os.path
import sys

import cryptography.fernet
from argon2.low_level import hash_secret_raw, Type
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import hashlib
from base64 import b64encode, b64decode

import db_manager
import file_enc
from db_manager import DbManager
from master_pass_db import MasterPassManager


class PasswordManager:
    def __init__(self):
        # Test string to be encrypted and checked if master password was correct
        self.TEST_STR = "Master password correct!"

        # Database manager instance
        self.db_manager = DbManager()
        # Master password manager instance
        self.master_passmgr = MasterPassManager()
        # Master password hash
        self.master_pass_hash = None
        # Bool if master password was set
        self.is_set = self.master_passmgr.is_set()

    def encrypt(self, plain_text, key: bytes, salt=None):
        """
        Encrypts plaintext using AES encryption and scrypt to derive key.
        :param salt: Optional: Salt used for encryption, if not provided, salt will be randomly generated.
        :param plain_text: Text to be encrypted.
        :param key: Key to be used for AES encryption, actual key will be derived from this value.
        :return: Dict of cipher text, salt, nonce and tag.
        """
        if salt is None:
            salt = get_random_bytes(AES.block_size)
        pk = hashlib.scrypt(key, salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        cipher_config = AES.new(pk, AES.MODE_GCM)
        cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
        return {
            'cipher_text': b64encode(cipher_text).decode('utf-8'),
            'salt'       : b64encode(salt).decode('utf-8'),
            'nonce'      : b64encode(cipher_config.nonce).decode('utf-8'),
            'tag'        : b64encode(tag).decode('utf-8')
        }

    def decrypt(self, enc_dict, key: bytes):
        """
        Decrypts cipher text using AES, verifies it and returns it.
        :param enc_dict: Dict containing cipher text, salt, nonce and tag in base64 format.
        :param key: Key to be used for decryption, actual key will be derived from this value.
        :return: bytes: Decrypted cipher text.
        """
        salt = b64decode(enc_dict['salt'])
        cipher_text = b64decode(enc_dict['cipher_text'])
        nonce = b64decode(enc_dict['nonce'])
        tag = b64decode(enc_dict['tag'])

        pk = hashlib.scrypt(key, salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
        cipher = AES.new(pk, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)
        return decrypted

    def hash_master_pass(self, password: bytes, salt):
        """
        Hashes master password.
        :param password: Master password for hashing.
        :param salt: Master password salt.
        :return: bytes: Hashed master password.
        """
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

    def setup(self, master_password):
        """
        Sets up testing file for authentication.
        :return:
        """
        # Get master password hash and generate salt for master password. Only salt is stored
        salt = self.master_passmgr.set_master_salt()
        if not salt:
            return False
        salt = self.master_passmgr.get_salt()
        self.master_pass_hash = self.hash_master_pass(master_password.encode('utf-8'), salt)
        result = self.encrypt(self.TEST_STR, self.master_pass_hash, salt)
        self.master_passmgr.set_test_str(result['cipher_text'], result['nonce'], result['tag'])
        return True

    def authenticate(self, master_password):
        """
        Authenticates user.
        :return: bool: True if supplied password is correct, False otherwise.
        """
        # Get master password hash and generate salt for master password. Only salt is stored
        self.master_pass_hash = self.hash_master_pass(master_password.encode('utf-8'), self.master_passmgr.get_salt())
        test_dict = self.master_passmgr.get_test_str()
        try:
            result = self.decrypt(test_dict, self.master_pass_hash)
        except ValueError:
            return False
        return self.TEST_STR == result.decode()

    def get_all_passwords(self):
        return self.db_manager.get_all()

    def logout(self):
        self.master_pass_hash = None

    def add(self, url, username, password, note=""):
        enc_pass = self.encrypt(password, self.master_pass_hash)
        self.db_manager.insert(username, key=self.master_pass_hash, password=enc_pass['cipher_text'], salt=enc_pass['salt'],
                               nonce=enc_pass['nonce'], tag=enc_pass['tag'], url=url, note=note)

    def get_by_id(self, row_id):
        r_id, url, username, password, note = self.db_manager.get_by_id(row_id)
        salt_dict, _ = db_manager.get_salt_by_id(row_id, self.master_pass_hash)
        if salt_dict is None:
            print('Error getting salts', file=sys.stderr)
            return row_id, url, username, password, note
        try:
            password = self.decrypt({
                'cipher_text': password,
                'salt': salt_dict['salt'],
                'nonce': salt_dict['nonce'],
                'tag': salt_dict['tag']
            }, self.master_pass_hash)
        except ValueError:
            password = None
            print('Error decrypting password', file=sys.stderr)
        return row_id, url, username, password, note

    def update_by_id(self, row_id, url, username, password, note=""):
        salt_dict, _ = db_manager.get_salt_by_id(row_id, self.master_pass_hash)
        if salt_dict is None:
            print('Error getting salts', file=sys.stderr)
            return False
        try:
            password_enc = self.encrypt(password, self.master_pass_hash)
        except ValueError:
            print('Error encrypting password', file=sys.stderr)
            return False
        return self.db_manager.update_by_id(self.master_pass_hash, row_id, username, password_enc['cipher_text'],
                                            url, note, password_enc['salt'], password_enc['nonce'], password_enc['tag'])

    def delete_by_id(self, row_id):
        self.db_manager.delete_by_id(row_id, self.master_pass_hash)
