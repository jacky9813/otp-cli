#!/usr/bin/env python3

import argparse
import sys
import hashlib
from datetime import datetime
import logging
import typing

from . import totp as totp_module
from . import hotp as hotp_module
from . import image
from . import otpauth_migrate


ALGORITHMS = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512
}


logger = logging.getLogger(__name__)


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
    parser.add_argument(
        "--log-level",
        choices=[l for l in logging._nameToLevel],
        default="INFO"
    )
    parser.add_argument(
        "--to-migration",
        action="store_true",
        help="Convert all found otp to Google Authenticator migration format."
    )

    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stderr,
        level=args.log_level
    )

    totps: typing.List[typing.Union[totp_module.TOTP, hotp_module.HOTP]] = [
        otp
        for image_file in args.image
        for otp in image.read_image(image_file)
    ]

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
        code = totp.get_code()
        print(f'{"Current Code":>20}: {code}')
        if not args.no_qr and not args.to_migration:
            totp.print_qrcode()

    if not args.no_qr and args.to_migration:
        print("=" * 20)
        migration = otpauth_migrate.OtpauthMigrate(
            otp_list=totps
        )
        print(
            f'{"Migration URI":>20}:',
            migration.to_uri() if args.show_secret else "*" * 40
        )
        migration.print_qrcode()

if __name__ == "__main__":
    main()
