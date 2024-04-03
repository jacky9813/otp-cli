import typing
import os
import urllib.parse

from pyzbar import pyzbar
from PIL import Image  # From package Pillow

from . import totp
from . import hotp
from . import otpauth_migrate


def read_image(
    path: typing.Union[str, os.PathLike]
) -> typing.Generator[typing.Union[totp.TOTP, hotp.HOTP], None, None]:
    for result in pyzbar.decode(Image.open(path)):
        try:
            uri_str = result.data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        uri = urllib.parse.urlparse(uri_str)
        if uri.scheme not in ["otpauth", "otpauth-migration"]:
            continue
        if uri.scheme == "otpauth" and uri.hostname == "totp":
            yield totp.TOTP(
                label=uri.path.strip("/"),
                **{
                    k: v[0]
                    for k, v in urllib.parse.parse_qs(uri.query).items()
                    if v
                }
            )
        elif uri.scheme == "otpauth" and uri.hostname == "hotp":
            yield hotp.HOTP(
                label=uri.path.strip("/"),
                **{
                    k: v[0]
                    for k, v in urllib.parse.parse_qs(uri.query).items()
                    if v
                }
            )
        elif uri.scheme == "otpauth-migration":
            migrate = otpauth_migrate.OtpauthMigrate.from_uri(uri_str)
            yield from migrate.otp_list
