#!/usr/bin/env python3

import argparse
import binascii
import sys
import hashlib
from datetime import datetime
import base64
import urllib.parse
import typing

from pyzbar import pyzbar
from PIL import Image  # From package Pillow
import qrcode

from . import totp as totp_module


ALGORITHMS = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512,
    "MD5": hashlib.md5
}

def main():
    "Output information about all TOTP QRCodes from image(s)."
    parser = argparse.ArgumentParser(
        description=main.__doc__
    )
    parser.add_argument(
        "image",
        help="The image containing the TOTP registering QR Code",
        nargs="+"
    )
    parser.add_argument(
        "--no-qr",
        action="store_true",
        help="Do not output a new QR Code."
    )
    parser.add_argument(
        "--show-secret",
        action="store_true",
        help="Display the secret."
    )

    args = parser.parse_args()

    totps: typing.List[totp_module.TOTP] = []

    # Reading QR Code from images
    for img_file in args.image:
        scanned = pyzbar.decode(Image.open(img_file))
        for info in scanned:
            try:
                uri_str = info.data.decode("utf-8")
            except UnicodeDecodeError:
                print("Detected a non-TOTP QR code", file=sys.stderr)
                continue
            uri = urllib.parse.urlparse(uri_str)
            if uri.scheme != "otpauth" or uri.netloc != "totp":
                print("Detected a non-TOTP QR code", file=sys.stderr)
                continue
            totps.append(totp_module.TOTP(
                label=uri.path.strip("/"),
                **{
                    k: v[0]
                    for k, v in urllib.parse.parse_qs(uri.query).items()
                    if v
                }
            ))

    if len(totps) == 0:
        print("No TOTP code has been detected.", file=sys.stderr)
        print(
            "Try to adjust the contrast/brightness of"
            "the image and feed the improved image here again!",
            file=sys.stderr
        )
        sys.exit(1)

    print(f'Total detected TOTP QR Code: {len(totps)}', file=sys.stderr)

    # Print out all information about scanned QR code
    for totp in totps:
        print("=" * 20)
        for field_name, field_value in totp.to_dict().items():
            if field_name in ["secret", "uri"]:
                if not args.show_secret:
                    print(f'{field_name:>20}: {"*" * 20}')
                else:
                    print(f'{field_name:>20}: {field_value}')
            elif field_name == "digits":
                field_value = int(field_value)
                print(
                    f'{field_name:>20}: {field_value}'
                    f'{" (invalid)" if field_value < 6 or field_value > 8 else ""}'
                )
            elif field_name == "algorithm":
                print(
                    f'{field_name:>20}: {field_value}',
                    "(invalid)" if field_value not in ALGORITHMS else ""
                    " (not supported by most OTP/MFA App)" if field_value != "SHA1" else ""
                )
            else:
                print(f'{field_name:>20}: {field_value}')
        print(f'{"URI":>20}: {totp.to_uri() if args.show_secret else "*"*30}')
        print(f'{"Current Time":>20}: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        try:
            code = totp.get_code()
        except (binascii.Error, ValueError):
            code = "Invalid TOTP"
        print(f'{"Current Code":>20}: {code}')
        if not args.no_qr:
            totp.print_qrcode()

if __name__ == "__main__":
    main()
