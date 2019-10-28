
Jenkins Utils
=============

.. image:: https://travis-ci.org/tarvitz/jenkins-utils.svg?branch=master
    :target: https://travis-ci.org/tarvitz/jenkins-utils

.. image:: https://coveralls.io/repos/github/tarvitz/jenkins-utils/badge.svg?branch=master
  :target: https://coveralls.io/github/tarvitz/jenkins-utils?branch=master

.. image:: https://badge.fury.io/py/jenkins-utils.svg
    :target: https://badge.fury.io/py/jenkins-utils

.. contents::
    :local:
    :depth: 2

Abstract
--------
Implements some jenkins utils in python way.

Notes
~~~~~
jenkins-utils does not support plain-credentials, ssh-credentials plugins,
so there's no option to encrypt/decrypt these data yet.

Requirements
------------

- Python 3.4+
- pycrypto (non windows systems)
- pycryptodomex (windows)

Usage
-----

Currently there's encrypt/decrypt operations implemented and gathered in convenient and
python developer friendly form.

As an example you an decrypt (or encrypt) message using Jenkins's master and hudson secret keys:

.. code-block:: bash

    $ python invoke.py --master-key master.key --hudson-secret-key hudson.util.Secret \
                       --action decrypt "{AQAAABAAAAAgd+820Q6QR4ABkf3JpXHacuO3zdj11o8JD/6VIJi8XjS9GJJyWquIYbNokyKKsIfN}"

    this is simple text to encrypt

    $ python invoke.py --master-key master.key --hudson-secret-key hudson.util.Secret \
                       --aes-type cbc --action encrypt "this is simple text to encrypt"
    {AQAAABAAAAAgfb9K8Kaq716l8SwGDqEFMRzm/3ynYDK7IsfI4C7BlVyMIlP/5JGfYK1n1Nc10VoD}
    $

.. note::

    - Master key is located at $JENKINS_HOME/secrets/master.key
    - Hudson key is located at $JENKINS_HOME/secrets/hudson.util.Secret

Advanced use
------------
reader.py

.. code-block:: python

    #!/usr/bin/env python3
    import sys
    import base64
    import argparse
    from lxml import etree
    from jenkins.utils import Secret


    def decrypt(opts):
        master_key = open(opts.master_key, 'rb').read()
        hudson_secret_key = open(opts.hudson_key, 'rb').read()
        secret = Secret(
            master_key=master_key, hudson_secret_key=hudson_secret_key
        )
        credentials = etree.fromstring(
            open(opts.credentials, 'rb').read()
        )
        for node in credentials.xpath('//com.cloudbees.plugins.credentials.'
                                      'impl.UsernamePasswordCredentialsImpl'):
            username, *_ = node.xpath('./username/text()')
            password_encoded, *_ = node.xpath('./password/text()')
            password = base64.decodebytes(password_encoded.encode('utf-8'))
            print(
                "Encrypted (username:password): ({}:{})".format(
                    username, secret.decrypt(password)
                )
            )


    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--credentials', dest='credentials',
                            required=True, help='jenkins credentials.xml file')
        parser.add_argument('-m', '--master-key', dest='master_key',
                            help='jenkins secrets master.key file', required=True)
        parser.add_argument('-H', '--hudson-secret-key', dest='hudson_key',
                            help='jenkins secrets hudson.util.Secret file')
        options = parser.parse_args()
        sys.exit(decrypt(options))


    if __name__ == '__main__':
        main()

.. code-block:: bash

    $ python reader.py -c credentials.xml -m master.key -H hudson.util.Secret

    Encrypted (username:password): (scm-bot:W9CA6qTajV)
    Encrypted (username:password): (artifactory-bot:vB9V9BtPN4)
    Encrypted (username:password): (git-bot:V32c5S8TnHCvmfr)
    ... and so on


References
----------
- |jenkins_secret_github|_
- |jenkins_python_decrypter|_


.. references

.. |jenkins_secret_github| replace:: Jenkins util/Secret.java sources
.. _jenkins_secret_github: https://github.com/jenkinsci/jenkins/blob/jenkins-2.89.4/core/src/main/java/hudson/util/Secret.java

.. |jenkins_python_decrypter| replace:: Jenkins python decrypter
.. _jenkins_python_decrypter: https://github.com/tweksteen/jenkins-decrypt/blob/master/decrypt.py

Obain secrets from Jenkins Master
---------------------------------

In case if you just need to receive unencrypted content of your jenkins secrets and you are an admin of your jenkins master you can simply use the following `script <https://devops.stackexchange.com/questions/2191/how-to-decrypt-jenkins-passwords-from-credentials-xml#8692>`_ at http://<your-jenkins-master>/script

.. code-block:: groovy

    com.cloudbees.plugins.credentials.SystemCredentialsProvider.getInstance().getCredentials().forEach{
      it.properties.each { prop, val ->
        println(prop + ' = "' + val + '"')
      }
      println("-----------------------")
    }

And obtain all requried data.


