# TOTP code extractor / rebuilder

This program is designed for those, for some reason, unable to scan the QR Code from the MFA provider.

## Requirements

* Python 3 (Tested with 3.9)
* Python packages in [requirements.txt](requirements.txt) `pip3 install -r requirements.txt` or `pip install -r requirements.txt`
* libzbar (for non Windows platform only)
    * Debian / Ubuntu: `apt install libzbar0`
    * RedHat / CentOS Stream / Rocky Linux / AlmaLinux: `dnf install zbar`
    * MacOS: `brew install zbar`

## Usage

```bash
python3 main.py --image path/to/the/image
```

## Issue

* Invalid secret is not detected.
