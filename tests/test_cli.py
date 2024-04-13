import re

import click.testing

import otp_cli
import otp_cli.cli


def test_cli_read_hotp(tmp_path):
    secret = b'12345678901234567890'
    initial_counter = 4321
    label = "HOTP"
    issuer = "Testing"

    expected_value: str = "091401"

    secret_file = tmp_path / "hotp.secret"
    hotp_file = tmp_path / "hotp.png"

    with open(secret_file, mode="wb") as secret_fd:
        secret_fd.write(secret)

    runner = click.testing.CliRunner()

    result_generate_qrcode = runner.invoke(
        otp_cli.cli.cli,
        [
            "build", "hotp", str(initial_counter), str(secret_file),
            "-i", issuer,
            "-l", label,
            "-o", str(hotp_file)
        ]
    )
    assert result_generate_qrcode.exit_code == 0


    result_check_qrcode = runner.invoke(
        otp_cli.cli.cli,
        ["read-image", str(hotp_file)]
    )
    assert result_check_qrcode.exit_code == 0
    assert expected_value in result_check_qrcode.output
    assert re.search(
        r"algorithm:\s*SHA1",
        result_check_qrcode.output
    )
    assert re.search(
        r"digits:\s*6",
        result_check_qrcode.output
    )
    assert re.search(
        r"counter:\s*" f'{initial_counter}',
        result_check_qrcode.output
    )
    assert re.search(
        r"label:\s*" f'{label}',
        result_check_qrcode.output
    )
    assert re.search(
        r"issuer:\s*" f'{issuer}',
        result_check_qrcode.output
    )
    assert re.search(
        r"URI:\s*\*+",
        result_check_qrcode.output
    )
