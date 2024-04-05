######################################
OTP (HOTP/TOTP) Command Line Interface
######################################

.. _otpauth URI scheme: https://www.ietf.org/archive/id/draft-linuxgemini-otpauth-uri-00.html
.. _otpauth-migration URI scheme: https://github.com/google/google-authenticator-android/issues/118

This program is designed for who want to rebuild the QR code of a TOTP.

The CLI support the following OTP format:

* `otpauth URI scheme`_ (Standard OTP)
* `otpauth-migration URI scheme` (Google Authenticator)


Requirements
============

* Python 3 (Tested with 3.9)
* libzbar (for non Windows platform only)
    * Debian / Ubuntu: ``apt install libzbar0``
    * RHEL and its derivatives / Fedora: ``dnf install zbar``
    * MacOS: ``brew install zbar``
* (Windows user only) Visual C++ Redistributable Packages for Visual Studio 2013
    * Download from `Official Site <https://www.microsoft.com/en-us/download/details.aspx?id=40784>`


Installation
============

.. code:: shell

    #!/bin/bash
    pip install --user git+https://github.com/jacky9813/totp-qrcode-analyzer


Usage
=====

Show help message:

.. code:: shell

    #!/bin/bash
    otp-cli --help


Read a QR code image and print OTP info:

.. code:: shell

    #!/bin/bash
    otp-cli read-image path/to/image-1 path/to/image-2


Read a QR code image and print OTP info with secret exposed:

.. code:: shell

    #!/bin/bash
    otp-cli read-image --show-secret path/to/image-1 path/to/image-2


Export all scanned OTP into Google Authenticator migration format:

.. code:: shell

    #!/bin/bash
    otp-cli read-image --to-migration path/to/image-1 path/to/image-2


Build an TOTP QR code:

.. code:: shell

    #!/bin/bash
    dd if=/dev/urandom bs=16 count=1 | otp-cli build totp - -o output.png
    # If you prefer SVG:
    # otp-cli build totp - -o output.svg
    #
    # Or show the QR Code in the console:
    # otp-cli build totp -


Limitations
===========

* Tilted QR Code maybe unable to read
* Some QR Code image may require some enhancement before reading
