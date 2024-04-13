"""
    Implementation of RFC 6238 TOTP: Time-Based One-Time Password Algorithm
"""

import typing
import time
import math

from . import hotp


class TOTP(hotp.HOTP):
    otp_type:str = "totp"

    _PROHIBITED_KEYS: typing.List[str] = [
        "period",
        "digits",
        "algorithm",
        "secret"
    ]


    def __init__(
        self,
        secret: typing.Union[bytes, str],
        *,
        period: int = 30,
        digits: typing.Literal[6, 8] = 6,
        algorithm: str = "sha1",
        **additional_info
    ):
        super().__init__(
            secret,
            counter=None,
            digits=digits,
            algorithm=algorithm,
            **additional_info
        )
        self._period = int(period)


    @property
    def C(self) -> bytes:
        t = math.floor(time.time() / self._period)
        return t.to_bytes(
            8,
            self._byteorder,
            signed=False
        )


    def to_dict(self) -> typing.Dict[str, typing.Union[str, int]]:
        return {
            k: v
            for k, v in {
                "secret": self.secret,
                "algorithm": self._digest.upper(),
                "digits": self.digits,
                "period": self._period,
                **self.additional_info
            }.items()
            if v
        }
