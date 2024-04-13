import base64
import typing
import urllib.parse

import pytest

import otp_cli


VERIFIER_TYPE = typing.Callable[
    [
        typing.Union[otp_cli.HOTP, otp_cli.TOTP, str],
        typing.Literal["totp", "hotp"],
        typing.Optional[bytes],
        typing.Optional[str],
        typing.Optional[int],
        typing.Optional[str],
        typing.Optional[str],
        typing.Literal["sha1", "sha256", "sha512"]
    ],
    None
]


@pytest.fixture
def verifier():
    def _verifier(
        otp: typing.Union[otp_cli.HOTP, otp_cli.TOTP, str],
        otp_type: typing.Literal["totp", "hotp"],
        secret: typing.Optional[bytes] = None,
        encoded_secret: typing.Optional[str] = None,
        counter: typing.Optional[int] = None,
        label: typing.Optional[str] = None,
        issuer: typing.Optional[str] = None,
        algorithm: typing.Literal["sha1", "sha256", "sha512"] = "sha1"
    ) -> None:
        if isinstance(otp, otp_cli.HOTP):
            otp = otp.to_uri()
        uri = urllib.parse.urlparse(otp)
        qs = urllib.parse.parse_qs(uri.query)
        assert uri.scheme == "otpauth"
        assert uri.hostname == otp_type
        assert not label or uri.path == f'/{label}'
        if otp_type == "hotp":
            assert str(counter) in qs.get("counter", [])
        if secret:
            encoded_secret = base64.b32encode(secret).decode().strip("=")
        if not encoded_secret:
            raise ValueError("Both secret and encoded_secret are empty.")
        assert encoded_secret in qs.get("secret", [])
        assert not issuer or issuer in qs.get("issuer", [])
        assert algorithm.upper() in qs.get("algorithm", [])
    return _verifier
