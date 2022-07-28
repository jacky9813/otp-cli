#!/usr/bin/env python3

import argparse
import sys
import urllib.parse
from pyzbar import pyzbar
from PIL import Image  # From package Pillow
import qrcode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="The image containing the TOTP registering QR Code")

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
                "issuer": qs["issuer"][0].strip() if "issuer" in qs else "Unknown",
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
        print(f'Name:    {totp["name"]}')
        print(f'Secret:  {totp["secret"]}')
        print(f'Issuer:  {totp["issuer"]}')
        print(f'URI:     {totp["uri"]}')
        qr = qrcode.QRCode()
        qr.add_data(totp["uri"])
        qr.print_ascii(invert=True)

if __name__ == "__main__":
    main()
