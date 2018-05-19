"""
Adopted from jenkins sources: core/src/main/java/hudson/util/Secret.java
Inspired by:

- https://stackoverflow.com/questions/25547381/what-password-encryption-jenkins-is-using/47020084#47020084  # NOQA
- https://github.com/tweksteen/jenkins-decrypt
"""
import re
import os
import hashlib
from struct import unpack, pack

from ... compat import AES

#: default jenkins magic
MAGIC = b'::::MAGIC::::'
#: by default
BLOCK_SIZE = DEFAULT_IV_LENGTH = 16
#: appears to be a random seed, but jenkins knows a drill
IV = b'\x00' * BLOCK_SIZE

#: CBC type
JENKINS_CIPHER_CBC_TYPE = b'\x01'


def new_iv(length: int = DEFAULT_IV_LENGTH) -> bytes:
    """
    generates new initialization vector
    """
    return os.urandom(length)


def pad(text: bytes, block_size=BLOCK_SIZE):
    size = (block_size - len(text) % block_size)
    return text + (chr(size) * size).encode('utf-8')


class Secret(object):
    """
    Jenkins Cipher provides encryption / decryption operations for:

    - AES.MODE_ECB (before security-304)
    - AES.MODE_CBC (after applying patches security-304)

    See https://jenkins.io/security/advisory/2017-02-01/ for more details
    """
    def __init__(self, master_key: bytes, hudson_secret_key: bytes):
        """
        Initiate jenkins cipher object with master and hudson secret keys
        for further encryption / decryption procedures

        :param master_key: jenkins master key
        :param hudson_secret_key: hudson secret key
        :raises AssertionError:
            - if MAGIC was not found in processed data
        """
        hashed_master_key = hashlib.sha256(master_key).digest()[:BLOCK_SIZE]
        cipher = AES.new(hashed_master_key, AES.MODE_ECB)
        result = cipher.decrypt(hudson_secret_key)
        assert MAGIC in result

        key = result[:-16]
        self.cipher_key = key[:16]

    @staticmethod
    def _is_payload_v1(raw) -> bool:
        """
        Detects if data has been encrypted with new approach

        :param bytes raw: encrypted string
        :return: True if data was encrypted with new approach
        """
        return raw[0] == 1

    def _decrypt_cbc(self, encrypted_text: bytes) -> str:
        """
        Decrypt data using AES.MODE_CBC

        encrypted text size::

            data {
                encryption type: byte, // byte
                iv_size: byte * 4, // int
                data_size: byte * 4, // int
                iv: byte * iv_size, // variable size
                block: byte * data_size // variable size
            }

        :param bytes encrypted_text: encrypted text to decipher
        :return: decrypted text based on cipher block chaining data
        """
        block = encrypted_text[1:]
        iv_size, *_ = unpack('>I', block[:4])

        #: strip iv length int block
        block = block[4:]
        #: using big-endian
        data_size, *_ = unpack('>I', block[:4])

        #: strip data length int block
        block = block[4:]
        iv = block[:iv_size]
        block = block[iv_size:]
        decrypter = AES.new(self.cipher_key, AES.MODE_CBC, iv)
        decrypted = decrypter.decrypt(block)
        padding = decrypted[-1]
        return decrypted[:len(decrypted) - padding].decode('utf-8')

    def _decrypt_ecb(self, encrypted_text: bytes) -> str:
        """
        Decrypt AES.MODE_ECB encrypted content (jenkins versions
        before security-304)

        :param encrypted_text:
        :return: decrypted text
        :raises AssertionError:
            - if MAGIC was not found in decrypted data taken from
              ``encrypted_text``
        """
        cipher = AES.new(self.cipher_key, AES.MODE_ECB)
        raw = cipher.decrypt(encrypted_text)
        assert MAGIC in raw
        return re.split(MAGIC.decode('utf-8'), raw.decode('utf-8'), 1)[0]

    def decrypt(self, encrypted_text: bytes) -> str:
        """
        Decrypts jenkins ``password_hash`` given in base64 encoded string to
        plain password, automatically detects old (ECB) and new (CBC)
        encrypted passwords.

        :param encrypted_text: base64 encoded password hash
            .. note::

                password hash should be in bytes form, not in base64 encoded
                string format.

        :return: plain password
        """
        if self._is_payload_v1(encrypted_text):
            return self._decrypt_cbc(encrypted_text)
        return self._decrypt_ecb(encrypted_text)

    def _encrypt_cbc(self, plain_text: str) -> bytes:
        """
        Encrypts text using AES.MODE_CBC
        (since https://jenkins.io/security/advisory/2017-02-01/)

        :param plain_text: text to encrypt
        :return: encrypted text
        """
        iv = new_iv()
        iv_size = pack('>I', len(iv))

        encrypter = AES.new(self.cipher_key, AES.MODE_CBC, iv)
        encrypted = encrypter.encrypt(
            pad(plain_text.encode('utf-8'))
        )
        encrypted_size = pack('>I', len(encrypted))

        payload = (
            JENKINS_CIPHER_CBC_TYPE + iv_size + encrypted_size +
            iv + encrypted
        )
        return payload

    def encrypt(self, plain_text: str, cipher_type: int=AES.MODE_ECB) -> bytes:
        """
        Encrypt ``plain`` string with jenkins hudson secret key

        :param plain_text: plain text to encrypt
        :param cipher_type: cipher type, one of the following:

        - AES.MODE_ECB
        - AES.MODE_CBC

        :return: encrypted text
        :raises NotImplementedError:

            - if cipher type is not supported yet

        .. note::

            encrypted text are not encoded to base64, so please pack it after
        """
        if cipher_type == AES.MODE_ECB:
            cipher = AES.new(self.cipher_key, AES.MODE_ECB)
            message = pad(plain_text.encode('utf-8') + MAGIC)
            return cipher.encrypt(message)
        elif cipher_type == AES.MODE_CBC:
            return self._encrypt_cbc(plain_text)
        else:
            raise NotImplementedError("Not implemented")
