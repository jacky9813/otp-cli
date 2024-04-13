import time

import otp_cli


def test_totp_c():
    totp = otp_cli.TOTP(
        b"Some random secret"
    )
    current_time = int(time.time())
    assert totp.C == (current_time // 30).to_bytes(8, "big", signed=False)
