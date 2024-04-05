import base64
import typing
import urllib.parse
import logging

from qrcode.main import QRCode

from . import otpauth_migrate_pb2
from . import totp
from . import hotp


T = typing.TypeVar("T")

DIGITS_MAPPING: typing.Dict[
    # otpauth_migrate_pb2.MigrationPayload.DigitCount,
    int,
    typing.Literal[6, 8]
] = {
    otpauth_migrate_pb2.MigrationPayload.DigitCount.DIGIT_COUNT_SIX: 6,
    otpauth_migrate_pb2.MigrationPayload.DigitCount.DIGIT_COUNT_EIGHT: 8
}

ALGORITHM_MAPPING: typing.Dict[
    # otpauth_migrate_pb2.MigrationPayload.Algorithm,
    int,
    str
] = {
    otpauth_migrate_pb2.MigrationPayload.Algorithm.ALGORITHM_SHA1: "SHA1",
    otpauth_migrate_pb2.MigrationPayload.Algorithm.ALGORITHM_SHA256: "SHA256",
    otpauth_migrate_pb2.MigrationPayload.Algorithm.ALGORITHM_SHA512: "SHA512",
    otpauth_migrate_pb2.MigrationPayload.Algorithm.ALGORITHM_MD5: "MD5"
}


logger = logging.getLogger(__name__)


def to_totp(
    parameters: otpauth_migrate_pb2.MigrationPayload.OtpParameters
) -> totp.TOTP:
    return totp.TOTP(
        secret=parameters.secret,
        digits=DIGITS_MAPPING.get(parameters.digits, 6),
        algorithm=ALGORITHM_MAPPING.get(parameters.algorithm, "sha1"),
        label=parameters.name,
        issuer=parameters.issuer
    )


def to_hotp(
    parameters: otpauth_migrate_pb2.MigrationPayload.OtpParameters
) -> hotp.HOTP:
    return hotp.HOTP(
        secret=parameters.secret,
        counter=parameters.counter,
        digits=DIGITS_MAPPING.get(parameters.digits, 6),
        algorithm=ALGORITHM_MAPPING.get(parameters.algorithm, "sha1"),
        label=parameters.name,
        issuer=parameters.issuer
    )


def type_unspecified(
    parameters: otpauth_migrate_pb2.MigrationPayload.OtpParameters
) -> hotp.HOTP:
    raise TypeError("OTP Type is not set")


OTP_TYPE_MAPPING: typing.Dict[
    # otpauth_migrate_pb2.MigrationPayload.OtpType,
    int,
    typing.Callable[
        [otpauth_migrate_pb2.MigrationPayload.OtpParameters],
        typing.Union[hotp.HOTP, totp.TOTP]
    ]
] = {
    otpauth_migrate_pb2.MigrationPayload.OtpType.OTP_TYPE_TOTP: to_totp,
    otpauth_migrate_pb2.MigrationPayload.OtpType.OTP_TYPE_HOTP: to_hotp,
    otpauth_migrate_pb2.MigrationPayload.OtpType.OTP_TYPE_UNSPECIFIED: type_unspecified
}


class OtpauthMigrate:
    def __init__(
        self,
        otp_list: typing.Iterable[typing.Union[totp.TOTP, hotp.HOTP]],
        version: int = 2,
        batch_size: int = 1,
        batch_index: int = 0,
        batch_id: int = 0
    ):
        self.otp_list = [o for o in otp_list]
        self.version = version
        self.batch_size = batch_size
        self.batch_index = batch_index
        self.batch_id = batch_id


    def __repr__(self) -> str:
        return f'<{type(self).__name__} [{len(self.otp_list)} of OTPs] object at 0x{id(self):x}>'


    @classmethod
    def from_uri(cls: typing.Type[T], uri: str) -> T:
        parsed_uri = urllib.parse.urlparse(uri)
        if parsed_uri.scheme != "otpauth-migration":
            raise ValueError("Not a valid otpauth-migration URI")
        parsed_qs = urllib.parse.parse_qs(parsed_uri.query)
        if "data" not in parsed_qs:
            raise ValueError("Query string does not contain data")

        migration = otpauth_migrate_pb2.MigrationPayload()
        migration.ParseFromString(
            base64.b64decode(parsed_qs["data"][0])
        )

        otp_list = [
            OTP_TYPE_MAPPING.get(otp.type)(otp) # type: ignore
            for otp in (migration.otp_parameters or [])
        ]
        return cls(
            otp_list,
            version=migration.version,
            batch_size=migration.batch_size,
            batch_index=migration.batch_index,
            batch_id=migration.batch_id
        )


    def to_uri(self) -> str:
        parameter_list = [
            otpauth_migrate_pb2.MigrationPayload.OtpParameters(
                secret=otp._shared_secret,
                name=otp.additional_info.get("label", None),
                issuer=otp.additional_info.get("issuer", None),
                algorithm=[
                    k
                    for k, v in ALGORITHM_MAPPING.items()
                    if v == otp._digest.upper()
                ][0], # type: ignore
                digits=[
                    k
                    for k, v in DIGITS_MAPPING.items()
                    if v == otp.digits
                ][0], # type: ignore
                type=(
                    otpauth_migrate_pb2.MigrationPayload.OtpType.OTP_TYPE_TOTP
                    if isinstance(otp, totp.TOTP)
                    else otpauth_migrate_pb2.MigrationPayload.OtpType.OTP_TYPE_HOTP
                ),
                counter=(
                    None
                    if isinstance(otp, totp.TOTP)
                    else otp._counter
                )
            )
            for otp in self.otp_list
            if (
                type(otp) == hotp.HOTP or
                (type(otp) == totp.TOTP and otp._period == 30)
            )
        ]

        migration = otpauth_migrate_pb2.MigrationPayload(
            otp_parameters=parameter_list,
            version=self.version,
            batch_size=self.batch_size,
            batch_index=self.batch_index,
            batch_id=self.batch_id
        )

        uri = urllib.parse.ParseResult(
            "otpauth-migration",
            "offline",
            "",
            "",
            urllib.parse.urlencode({
                "data": base64.b64encode(
                    migration.SerializeToString()
                ).decode()
            }),
            ""
        )

        return urllib.parse.urlunparse(uri)


    def to_qrcode_image(
        self,
        image_factory = None
    ):
        uri = self.to_uri()
        qr = QRCode(image_factory=image_factory)
        qr.add_data(uri)
        return qr.make_image()


    def print_qrcode(self) -> None:
        qr = QRCode()
        qr.add_data(self.to_uri())
        qr.print_ascii(invert=True)
