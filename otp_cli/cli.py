#!/usr/bin/env python3

import os
import hashlib
from datetime import datetime
import logging
import typing
import re
import importlib.metadata

import click
import qrcode
import qrcode.image.pure
import qrcode.image.svg

from . import totp as totp_module
from . import hotp as hotp_module
from . import images
from . import otpauth_migrate


ALGORITHMS = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512
}


logger = logging.getLogger(__name__)


def show_otp_info(
    otp: typing.Union[totp_module.TOTP, hotp_module.HOTP],
    show_secret: bool = False
) -> None:
    for field_name, field_value in otp.to_dict().items():
        if field_name in ["secret", "uri"]:
            if not show_secret:
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
    print(f'{"URI":>20}: {otp.to_uri() if show_secret else "*"*30}')
    print(f'{"Current Time":>20}: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    code = otp.get_code()
    print(f'{"Current Code":>20}: {code}')


def get_image_factory(output: str):
    ext = os.path.splitext(output)[1].lower().strip(".")
    if ext in ["png", "-"]:
        return None
    elif ext == "svg":
        return qrcode.image.svg.SvgPathImage
    raise ValueError("Unknown output file extension")


def print_version(
    ctx: click.Context,
    param: click.Parameter,
    value: typing.Optional[str] = None
):
    if not value or ctx.resilient_parsing:
        return
    print(importlib.metadata.version("otp_cli"))
    ctx.exit()


@click.group()
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False,
    is_eager=True, help="Show the application version and exit."
)
def cli():
    """
    A CLI for managing TOTP and HOTP tokens and QR code.
    """


SET_COUNTER_RE = re.compile(r"(?P<relative>\+|-)?(?P<new_counter>\d+)")


def get_counter_modifier(
    set_counter: str
) -> typing.Callable[[hotp_module.HOTP], None]:
    if not set_counter:
        return lambda _: None
    set_counter_match = SET_COUNTER_RE.match(set_counter)

    if not set_counter_match:
        raise ValueError(
            'Invalid value for set_counter. Must be ("+"/"-"/"")<integer>.'
        )

    relative = set_counter_match.group("relative")
    new_counter = int(set_counter_match.group("new_counter"))

    def counter_modifier(hotp: hotp_module.HOTP) -> None:
        # Cannot use isinstance here as it checks for subclasses.
        if type(hotp) != hotp_module.HOTP:
            return
        if relative == "+":
            hotp.set_counter(hotp._counter + new_counter)
        elif relative == "-":
            hotp.set_counter(hotp._counter - new_counter)
        elif not relative:
            hotp.set_counter(new_counter)
        else:
            raise ValueError(
                "relative must be either empty, plus sign or minus sign"
            )

    return counter_modifier


@cli.command()
@click.argument(
    "image",
    type=click.Path(exists=True, dir_okay=False),
    nargs=-1
)
@click.option(
    "--qr/--no-qr",
    default=True,
    is_flag=True,
    help="Show/hide the rebuilt QR code."
)
@click.option(
    "--show-secret",
    default=False,
    is_flag=True,
    help="Show the Base-32 encoded secret for the OTP."
)
@click.option(
    "--to-migration",
    default=False,
    is_flag=True,
    help="Output all OTP into one OTP migration format (for Google "
         "Authenticator)"
)
@click.option(
    "--set-counter",
    help="For HOTP, reset the counter to the specified value. When the number "
         "is prefixed by a plus or minus sign, this indicates the relative "
         "counter number instead of an absolute number."
)
def read_image(
    image: typing.Iterable[str],
    qr: bool = True,
    show_secret: bool = False,
    to_migration: bool = False,
    set_counter: str = ""
):
    """
    Reads IMAGE files and rebuild the QR code for the OTP.
    """
    otp_list: typing.List[typing.Union[totp_module.TOTP, hotp_module.HOTP]] = [
        otp
        for filepath in image
        for otp in images.read_image(filepath)
    ]
    hotp_counter_modifier = get_counter_modifier(set_counter)
    for otp in otp_list:
        print("=" * 20)
        hotp_counter_modifier(otp)
        show_otp_info(otp, show_secret)
        if qr and not to_migration:
            otp.print_qrcode()
    if qr and to_migration:
        print("=" * 20)
        migration = otpauth_migrate.OtpauthMigrate(
            otp_list
        )
        print(
            f'{"Migration URI":>20}:',
            migration.to_uri() if show_secret else ("*" * 40)
        )
        migration.print_qrcode()


@cli.group()
def build():
    "Build an OTP QRCode"


@build.command()
@click.argument(
    "secret_from",
    type=click.File(mode="rb")
)
@click.option(
    "--label", "-l",
    help="The label for this TOTP token."
)
@click.option(
    "--issuer", "-i",
    help="The name of the TOTP token issuer."
)
@click.option(
    "--algorithm",
    type=click.Choice(["sha1", "sha256", "sha512"]),
    default="sha1",
    help="The algorithm to be used. Some authenticator app may have limited "
         "support for algorithm other than sha1. Default is sha1."
)
@click.option(
    "--period",
    type=int,
    default=30,
    help="How often (in seconds) a TOTP code changes. Default is 30."
)
@click.option(
    "--digits",
    type=click.Choice(["6", "8"]),
    default="6",
    help="How many digits a result should be. Default is 6."
)
@click.option(
    "--to-migration",
    is_flag=True,
    help="Generate a migration QR code instead of standard one. (Google "
    "Authenticator). --period must be 30."
)
@click.option(
    "--output", "-o",
    type=click.Path(writable=True, dir_okay=False, allow_dash=True),
    default="-",
    help="The output path. Only PNG and SVG file is supported. Shows on "
         "console when \"-\" is passed here. Default is \"-\"."
)
def totp(
    secret_from: typing.BinaryIO,
    label: typing.Optional[str] = None,
    issuer: typing.Optional[str] = None,
    algorithm: str = "sha1",
    period: int = 30,
    digits: str = "6",
    to_migration: bool = False,
    output: str = "-"
):
    """
    Build a TOTP QR code.

    \b
    SECRET_FROM     This should be a file path that contains the raw secret in 
                    binary format. Pass "-" for reading from stdin.
    """
    secret = secret_from.read()
    if not secret:
        raise ValueError("Unable to read or the secret file is empty.")

    otp_output = totp_module.TOTP(
        secret,
        period=period,
        digits=int(digits), # type: ignore
        algorithm=algorithm,
        **{
            k: v
            for k, v in {"label": label, "issuer": issuer}.items()
            if v
        }
    )

    if to_migration:
        otp_output = otpauth_migrate.OtpauthMigrate(
            [otp_output]
        )

    if output == "-":
        otp_output.print_qrcode()
    else:
        image = otp_output.to_qrcode_image(
            image_factory=get_image_factory(output)
        )
        with open(output, mode="wb") as output_fd:
            image.save(output_fd)


@build.command()
@click.argument(
    "counter",
    type=int
)
@click.argument(
    "secret_from",
    type=click.File(mode="rb")
)
@click.option(
    "--label", "-l",
    help="The label for this TOTP token."
)
@click.option(
    "--issuer", "-i",
    help="The name of the TOTP token issuer."
)
@click.option(
    "--algorithm",
    type=click.Choice(["sha1", "sha256", "sha512"]),
    default="sha1",
    help="The algorithm to be used. Some authenticator app may have limited "
         "support for algorithm other than sha1. Default is sha1."
)
@click.option(
    "--digits",
    type=click.Choice(["6", "8"]),
    default="6",
    help="How many digits a result should be. Default is 6."
)
@click.option(
    "--to-migration",
    is_flag=True,
    help="Generate a migration QR code instead of standard one. (Google "
    "Authenticator). --period must be 30."
)
@click.option(
    "--output", "-o",
    type=click.Path(writable=True, dir_okay=False, allow_dash=True),
    default="-",
    help="The output path. Only PNG and SVG file is supported. Shows on "
         "console when \"-\" is passed here. Default is \"-\"."
)
def hotp(
    counter: int,
    secret_from: typing.BinaryIO,
    label: typing.Optional[str] = None,
    issuer: typing.Optional[str] = None,
    algorithm: str = "sha1",
    digits: str = "6",
    to_migration: bool = False,
    output: str = "-"
):
    """
    Build a HOTP QR code.

    \b
    COUNTER         A non-negative integer that specifies the amount of
                    generated HOTP tokens
    SECRET_FROM     This should be a file path that contains the raw secret in 
                    binary format. Pass "-" for reading from stdin.
    """
    secret = secret_from.read()
    if not secret:
        raise ValueError("Unable to read or the secret file is empty.")

    otp_output = hotp_module.HOTP(
        secret,
        counter=counter,
        digits=int(digits), # type: ignore
        algorithm=algorithm,
        **{
            k: v
            for k, v in {"label": label, "issuer": issuer}.items()
            if v
        }
    )

    if to_migration:
        otp_output = otpauth_migrate.OtpauthMigrate(
            [otp_output]
        )

    if output == "-":
        otp_output.print_qrcode()
    else:
        image = otp_output.to_qrcode_image(
            image_factory=get_image_factory(output)
        )
        with open(output, mode="wb") as output_fd:
            image.save(output_fd)


def main():
    cli()


if __name__ == "__main__":
    cli()
