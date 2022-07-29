#!/usr/bin/env python3

import argparse
import sys
import urllib.parse
from pyzbar import pyzbar
from PIL import Image  # From package Pillow
import qrcode
import otp
import hashlib
from datetime import datetime


ALGORITHMS = {
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="The image containing the TOTP registering QR Code")
    parser.add_argument("--no-qr", action="store_true", help="Do not output a new QR Code.")

    args = parser.parse_args()

    scanned = pyzbar.decode(Image.open(args.image))

    totps = []

    for info in scanned:
        try:
            uri_str = info.data.decode("utf-8")
        except:
            print("Detected a non-TOTP QR code", file=sys.stderr)
            continue
        uri = urllib.parse.urlparse(uri_str)
        if uri.scheme != "otpauth" or uri.netloc != "totp":
            print("Detected a non-TOTP QR code", file=sys.stderr)
            continue
        qs = urllib.parse.parse_qs(uri.query)
        if "secret" in qs:
            totps.append({
                "name": urllib.parse.unquote(uri.path[1:]),
                "secret": qs["secret"][0],
                "issuer": qs.get("issuer", ["Unknown"])[0].strip(),
                "algorithm": qs.get("algorithm", ["sha1"])[0].lower(),
                "digits": int(qs.get("digits", ["6"])[0]),
                "period": int(qs.get("period", ["30"])[0]),
                "uri": uri_str
            })
        else:
            print("Detected a totp URI but has no secret string.")
    
    if len(totps) == 0:
        print("No TOTP code has been detected.", file=sys.stderr)
        print("Try to adjust the contrast/brightness of the image and feed the improved image here again!", file=sys.stderr)
        exit(1)

    print(f'Total detected TOTP QR Code: {len(totps)}', file=sys.stderr)

    for totp in totps:
        print("=" * 20)
        print(f'Name:           {totp["name"]}')
        print(f'Secret:         {totp["secret"]}')
        print(f'Issuer:         {totp["issuer"]}')
        print(f'Hash Algorithm: {totp["algorithm"]}')
        print(f'OTP Digits:     {totp["digits"]}')
        print(f'Change Period:  {totp["period"]}')
        print(f'URI:            {totp["uri"]}')
        print(f'Current Time:   {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'Current Code:   {otp.totp(totp["secret"], digits=totp["digits"], period=totp["period"], digest=ALGORITHMS[totp["algorithm"]])}')
        if not args.no_qr:
            qr = qrcode.QRCode()
            qr.add_data(totp["uri"])
            qr.print_ascii(invert=True)

if __name__ == "__main__":
    main()
