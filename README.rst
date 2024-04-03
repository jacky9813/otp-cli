###############################
TOTP code extractor / rebuilder
###############################

This program is designed for who want to rebuild the QR code of a TOTP.


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

.. code:: shell

    #!/bin/bash
    totp path/to/image-1 path/to/image-2


Print the TOTP secret:

.. code:: shell

    #!/bin/bash
    totp --show-secret path/to/image-1 path/to/image-2


Show help message:

.. code:: shell

    #!/bin/bash
    totp --help


Limitations
===========

* Tilted QR Code maybe unable to read
* Some QR Code image may require some enhancement before reading
