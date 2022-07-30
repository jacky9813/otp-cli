"""
    Implementation of HOTP (RFC4226) and TOTP (RFC6238)
"""
import hmac
import hashlib
import base64
import time
import math
from typing import Any, Callable, Union


ENDIAN = "big"

def hotp(
    K: bytes,
    C: bytes,
    digits: int = 6,
    digest: Callable[..., Any] = hashlib.sha1
) -> str:
    """HMAC-Based One-Time Password (RFC4226)"""
    if digest not in [hashlib.sha1, hashlib.sha256, hashlib.sha512]:
        raise ValueError("Unsupported digest algorithm")
    if digits < 6 or digits > 8:
        raise ValueError("The output digits must be between 6 and 8 (inclusive)")
    HS = hmac.new(K, C, digest).digest()
    Sbits = HS[ (HS[19] & 0x0F) : ((HS[19] & 0x0F) + 4)]
    Snum = int.from_bytes(Sbits, "big", signed=False) & 0x7FFFFFFF
    return (("0" * digits) + str(Snum % (10 ** digits)))[-digits:]

def totp(
    secret: str,
    timestamp: Union[None, int, float] = None,
    digits: int = 6,
    period: int = 30,
    T0: int = 0,
    digest: Callable[..., Any] = hashlib.sha1
) -> str:
    """Time-Based One-Time Password (RFC6238)"""
    if timestamp is None:
        T = math.floor((time.time() - T0) / period)
    else:
        T = math.floor((timestamp - T0) / period)
    return hotp(
        base64.b32decode(secret),
        T.to_bytes(8, "big", signed=False),
        digits = digits,
        digest = digest
    )

if __name__ == "__main__":
    print(f'{totp("JBSWY3DPEHPK3PXP"):06d}')
