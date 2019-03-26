import os
import sys
import base64
import argparse

import logging

from . import Secret
from ... compat import AES


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


ACTION_ENCRYPT = 'encrypt'
ACTION_DECRYPT = 'decrypt'
ACTIONS = (
    ACTION_ENCRYPT, ACTION_DECRYPT
)
DEFAULT_ACTION = ACTION_ENCRYPT
EXIT_OK = 0

ENC_ECB = 'ecb'
ENC_CBC = 'cbc'
ENC_TYPES = (ENC_ECB, ENC_CBC)
ENC_TYPE_MAP = {
    ENC_ECB: AES.MODE_ECB,
    ENC_CBC: AES.MODE_CBC
}


def get_absolute_path(relative_path):
    """
    gets absolute path in respect of running operating system (useful to use
    it for volumes registration and so other basic operations)

    :param str relative_path: relative path to get absolute path for docker
        volume. Depending on OS it could be different.
    :rtype: str
    :return: str
    """
    return os.path.normcase(os.path.abspath(relative_path))


def main(opts):
    master_key_location = get_absolute_path(opts.master_key)
    hudson_secret_key_location = get_absolute_path(opts.hudson_secret_key)
    master_key = open(master_key_location, 'rb').read()
    hudson_secret_key = open(hudson_secret_key_location, 'rb').read()
    cipher = Secret(hudson_secret_key=hudson_secret_key,
                    master_key=master_key)
    for message in opts.messages:
        if opts.action == ACTION_ENCRYPT:
            cipher_type = ENC_TYPE_MAP.get(opts.aes_type,
                                           ENC_TYPE_MAP[ENC_ECB])
            encrypted = cipher.encrypt(message, cipher_type=cipher_type)
            b64_encoded = base64.b64encode(encrypted).decode('utf-8')
            if opts.aes_type == ENC_CBC:
                b64_encoded = '{%s}' % b64_encoded
            print(b64_encoded)
        elif opts.action == ACTION_DECRYPT:
            print(cipher.decrypt(base64.b64decode(message)))
        else:
            pass
    return EXIT_OK


def execute():
    parser = argparse.ArgumentParser(
        prog='jenkins_cipher',
        description='cipher operations (encrypt / decrypt)'
    )
    parser.add_argument(nargs='*', dest='messages', type=str,
                        help='passwords split by space to encrypt',
                        metavar='text')
    parser.add_argument(
        '--action', dest='action',
        choices=ACTIONS,
        default=DEFAULT_ACTION,
        help='action to perform, default is `%s`' % DEFAULT_ACTION,
        required=False
    )
    parser.add_argument(
        '--aes-type', dest='aes_type',
        default=ENC_ECB,
        choices=ENC_TYPES,
        help='encryption type, default: %(default)s, '
             'available choices: %(choices)s '
             'Jenkins before 2017-02-01 uses ECB, newer jenkins uses CBC, '
             'see https://jenkins.io/security/advisory/2017-02-01/ for details'
    )
    parser.add_argument('--master-key', dest='master_key',
                        required=True,
                        help='master key location')
    parser.add_argument('--hudson-secret-key', dest='hudson_secret_key',
                        help='hudson secret key')
    options = parser.parse_args()
    sys.exit(main(options))


if __name__ == '__main__':
    execute()
