#!/usr/bin/env python3
"""
.. synopsis: Development invoke script, helps with debug purpose
.. author:: Nickolas Fox <tarvitz@blacklibrary.ru>
"""

import sys
from jenkins.utils.secret import __main__


def check():
    if sys.version_info[:2] < (3, 4):
        print("jenkins-cipher requires python-3.4+, exiting ..")
        sys.exit(-1)


def main():
    sys.exit(__main__.execute())


if __name__ == '__main__':
    main()
