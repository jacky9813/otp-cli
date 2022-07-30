#!/usr/bin/env python3

import argparse
import binascii
import sys
import hashlib
from datetime import datetime
import base64
import urllib.parse
from pyzbar import pyzbar
from PIL import Image  # From package Pillow
import qrcode
import otp


ALGORITHMS = {
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512
}

def main():
    "Output information about all TOTP QRCodes from the image."
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
    parser.add_argument(
        "--show-qr-stat",
        action="store_true",
        help="Show the information about source QR code"
    )

    args = parser.parse_args()

    totps = []

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
            qs = urllib.parse.parse_qs(uri.query)
            if "secret" in qs:
                totps.append({
                    "image_file": img_file,
                    "name": urllib.parse.unquote(uri.path[1:]),
                    "secret": qs["secret"][0],
                    "issuer": qs.get("issuer", ["Unknown"])[0].strip(),
                    "algorithm": qs.get("algorithm", ["sha1"])[0].lower(),
                    "digits": int(qs.get("digits", ["6"])[0]),
                    "period": int(qs.get("period", ["30"])[0]),
                    "qrcode": info,
                    "uri": uri_str
                })
                try:
                    base64.b32decode(totps[-1]["secret"])
                except binascii.Error:
                    totps[-1]["secret"] = f'{totps[-1]["secret"]} (Invalid)'
            else:
                print("Detected a totp URI but has no secret string.")

    if len(totps) == 0:
        print("No TOTP code has been detected.", file=sys.stderr)
        print(
            "Try to adjust the contrast/brightness of"
            "the image and feed the improved image here again!",
            file=sys.stderr
        )
        sys.exit(1)

    print(f'Total detected TOTP QR Code: {len(totps)}', file=sys.stderr)

    for totp in totps:
        print("=" * 20)
        for field_name, field_value in totp.items():
            if field_name in ["secret", "uri"] and not args.show_secret:
                valid_secret = True
                if field_name == "secret":
                    try:
                        base64.b32decode(field_value)
                    except binascii.Error:
                        valid_secret = False
                print(f'{field_name:>20}: {"*" * len(field_value)}{"" if valid_secret else " (invalid)"}')
            elif field_name == "digits":
                print(
                    f'{field_name:>20}: {field_value}'
                    f'{" (invalid)" if field_value < 6 or field_value > 8 else ""}'
                )
            elif field_name == "algorithm":
                print(
                    f'{field_name:>20}: {field_value}' +
                    f'{" (invalid)" if field_value not in ALGORITHMS else ""}'
                    f'{" (not supported by most OTP/MFA App)" if field_value != "sha1" else ""}'
                )
            elif field_name == "qrcode":
                if args.show_qr_stat:
                    for qr_attr in ["type", "orientation", "quality"]:
                        print(f'{f"Code {qr_attr}":>20}: {getattr(field_value, qr_attr)}')
            else:
                print(f'{field_name:>20}: {field_value}')
        print(f'{"Current Time":>20}: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        try:
            code = otp.totp(
                totp["secret"],
                digits=totp["digits"],
                period=totp["period"],
                digest=ALGORITHMS[totp["algorithm"]]
            )
        except (binascii.Error, ValueError):
            code = "Invalid TOTP"
        print(f'{"Current Code":>20}: {code}')
        if not args.no_qr:
            qr = qrcode.QRCode()
            qr.add_data(totp["uri"])
            qr.print_ascii(invert=True)

if __name__ == "__main__":
    main()
