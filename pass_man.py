import re
import string
import secrets
import sys

from argon2.low_level import hash_secret_raw, Type
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode

import db_manager
from db_manager import DbManager
from master_pass_db import MasterPassManager


def generate_password(length):
    """
    Generates randomized strong password
    :param length: Length of the password (must be at least 8)
    :return: Generated password in string format
    """
    # Minimum length
    if length < 8:
        return None

    # Character set
    chars = string.ascii_letters + string.digits + "@$!%*?&#"
    return ''.join(secrets.choice(chars) for _ in range(length))


def verify_pass_strength(password: str):
    """
    Verifies password strength
    :param password: Password to be verified in string format
    :return: True if password complies with policy, False otherwise
    """
    if len(password) < 8:
        return False
    match = re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#]).+$", password)
    return match is not None


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
        Encrypts plaintext using AES encryption and Argon2id to derive key.
        :param salt: Optional: Salt used for encryption, if not provided, salt will be randomly generated.
        :param plain_text: Text to be encrypted.
        :param key: Key to be used for AES encryption, actual key will be derived from this value.
        :return: Dict of cipher text, salt, nonce and tag.
        """
        if salt is None:
            salt = get_random_bytes(16)
        pk = self.hash_master_pass(key, salt, 32)

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

        pk = self.hash_master_pass(key, salt, 32)
        cipher = AES.new(pk, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)
        return decrypted

    def hash_master_pass(self, password: bytes, salt, hash_len=32):
        """
        Hashes master password.
        :param hash_len: Length of the final hash
        :param password: Master password for hashing.
        :param salt: Master password salt.
        :return: bytes: Hashed master password.
        """
        time_cost = 3
        memory_cost = 65536
        parallelism = 4
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
        :param master_password: Master password to encrypt the testing string
        :return: True if everything is set correctly, False on error or when weak password is supplied
        """
        if not verify_pass_strength(master_password):
            print("Weak master password!", file=sys.stderr)
            return False
        # Get master password hash and generate salt for master password. Only salt is stored
        salt = self.master_passmgr.set_master_salt()
        if not salt:
            print("Error generating salt!", file=sys.stderr)
            return False
        salt = self.master_passmgr.get_salt()
        self.master_pass_hash = self.hash_master_pass(master_password.encode('utf-8'), salt)
        result = self.encrypt(self.TEST_STR, self.master_pass_hash, salt)
        self.master_passmgr.set_test_str(result['cipher_text'], result['nonce'], result['tag'])
        self.is_set = True
        return True

    def authenticate(self, master_password):
        """
        Authenticates user.
        :param master_password: Master password used to try decryption of the testing string.
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
        """
        Returns all rows from the database
        :return: List of tuples containing rows in the database
        """
        return self.db_manager.get_all()

    def logout(self):
        """
        When logging out, remove master password hash from memory
        :return:
        """
        self.master_pass_hash = None

    def add(self, url, username, password, note=""):
        """
        Adds password to database
        :param url: URL or domain of a service, for which the password is used
        :param username: Username for given service
        :param password: Plain text password for given service
        :param note: User's note
        :return:
        """
        enc_pass = self.encrypt(password, self.master_pass_hash)
        self.db_manager.insert(username, password=enc_pass['cipher_text'], salt=enc_pass['salt'],
                               nonce=enc_pass['nonce'], tag=enc_pass['tag'], url=url, note=note)

    def get_by_id(self, row_id):
        """
        Returns one row from the database with given id
        :param row_id: ID of the row that is needed
        :return: Tuple of (row_id, url, username, password, note), password is already decrypted
        """
        r_id, url, username, password, salt, nonce, tag, note = self.db_manager.get_by_id(row_id)
        try:
            password = self.decrypt({
                'cipher_text': password,
                'salt': salt,
                'nonce': nonce,
                'tag': tag
            }, self.master_pass_hash)
        except ValueError:
            password = None
            print('Error decrypting password', file=sys.stderr)
        return row_id, url, username, password, note

    def update_by_id(self, row_id, url, username, password, note=""):
        """
        Updates a row with given id
        :param row_id: ID of a row to update
        :param url: URL or domain of a service, for which the password is used
        :param username: Username for given service
        :param password: Password for given service
        :param note: User's note'
        :return: True if updated successfully, False otherwise
        """
        salt_dict, _ = db_manager.get_salt_by_id(row_id, self.master_pass_hash)
        if salt_dict is None:
            print('Error getting salts', file=sys.stderr)
            return False
        try:
            password_enc = self.encrypt(password, self.master_pass_hash)
        except ValueError:
            print('Error encrypting password', file=sys.stderr)
            return False
        return self.db_manager.update_by_id(row_id, username, password_enc['cipher_text'],
                                            url, note, password_enc['salt'], password_enc['nonce'], password_enc['tag'])

    def delete_by_id(self, row_id):
        """
        Deletes a row from the database
        :param row_id: ID of row to be deleted
        :return:
        """
        self.db_manager.delete_by_id(row_id)
