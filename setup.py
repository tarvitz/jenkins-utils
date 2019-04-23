import os
from setuptools import find_packages, setup

PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))


def relative_path(path, base_dir=PACKAGE_ROOT):
    return os.path.join(base_dir, path)


requirements = [
    'pycryptodomex>=3.6.1;platform_system=="Windows"',
    'pycrypto>=2.6.1;platform_system != "Windows"'
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development :: Libraries',
]

test_requirements = ['tox>=2.9.1']
setup_requirements = ['setuptools-scm']


def readme():
    with open(relative_path('README.rst'), 'r') as f:
        return f.read()


setup(
    author='Nickolas Fox',
    author_email='tarvitz@blacklibrary.ru',
    url="https://github.com/tarvitz/jenkins-secret",
    name='jenkins-utils',
    install_requires=requirements,
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    classifiers=classifiers,
    description='Jenkins Utils',
    long_description=readme(),
    keywords='jenkins cipher secret tools utils aes ecb cbc',
    python_requires='>=3',
    packages=find_packages(),
    platforms=['any'],
    include_package_data=True,
    zip_safe=False,
    use_scm_version={
         'write_to': 'jenkins/_version.py',
    },
    entry_points={
        'console_scripts': [
            'jenkins-secret = jenkins.utils.secret.__main__:execute',
        ]
    },
)
