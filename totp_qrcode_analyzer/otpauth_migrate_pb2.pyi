from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MigrationPayload(_message.Message):
    __slots__ = ("otp_parameters", "version", "batch_size", "batch_index", "batch_id")
    class Algorithm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALGORITHM_UNSPECIFIED: _ClassVar[MigrationPayload.Algorithm]
        ALGORITHM_SHA1: _ClassVar[MigrationPayload.Algorithm]
        ALGORITHM_SHA256: _ClassVar[MigrationPayload.Algorithm]
        ALGORITHM_SHA512: _ClassVar[MigrationPayload.Algorithm]
        ALGORITHM_MD5: _ClassVar[MigrationPayload.Algorithm]
    ALGORITHM_UNSPECIFIED: MigrationPayload.Algorithm
    ALGORITHM_SHA1: MigrationPayload.Algorithm
    ALGORITHM_SHA256: MigrationPayload.Algorithm
    ALGORITHM_SHA512: MigrationPayload.Algorithm
    ALGORITHM_MD5: MigrationPayload.Algorithm
    class DigitCount(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DIGIT_COUNT_UNSPECIFIED: _ClassVar[MigrationPayload.DigitCount]
        DIGIT_COUNT_SIX: _ClassVar[MigrationPayload.DigitCount]
        DIGIT_COUNT_EIGHT: _ClassVar[MigrationPayload.DigitCount]
    DIGIT_COUNT_UNSPECIFIED: MigrationPayload.DigitCount
    DIGIT_COUNT_SIX: MigrationPayload.DigitCount
    DIGIT_COUNT_EIGHT: MigrationPayload.DigitCount
    class OtpType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OTP_TYPE_UNSPECIFIED: _ClassVar[MigrationPayload.OtpType]
        OTP_TYPE_HOTP: _ClassVar[MigrationPayload.OtpType]
        OTP_TYPE_TOTP: _ClassVar[MigrationPayload.OtpType]
    OTP_TYPE_UNSPECIFIED: MigrationPayload.OtpType
    OTP_TYPE_HOTP: MigrationPayload.OtpType
    OTP_TYPE_TOTP: MigrationPayload.OtpType
    class OtpParameters(_message.Message):
        __slots__ = ("secret", "name", "issuer", "algorithm", "digits", "type", "counter")
        SECRET_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        ISSUER_FIELD_NUMBER: _ClassVar[int]
        ALGORITHM_FIELD_NUMBER: _ClassVar[int]
        DIGITS_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        COUNTER_FIELD_NUMBER: _ClassVar[int]
        secret: bytes
        name: str
        issuer: str
        algorithm: MigrationPayload.Algorithm
        digits: MigrationPayload.DigitCount
        type: MigrationPayload.OtpType
        counter: int
        def __init__(self, secret: _Optional[bytes] = ..., name: _Optional[str] = ..., issuer: _Optional[str] = ..., algorithm: _Optional[_Union[MigrationPayload.Algorithm, str]] = ..., digits: _Optional[_Union[MigrationPayload.DigitCount, str]] = ..., type: _Optional[_Union[MigrationPayload.OtpType, str]] = ..., counter: _Optional[int] = ...) -> None: ...
    OTP_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    BATCH_INDEX_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    otp_parameters: _containers.RepeatedCompositeFieldContainer[MigrationPayload.OtpParameters]
    version: int
    batch_size: int
    batch_index: int
    batch_id: int
    def __init__(self, otp_parameters: _Optional[_Iterable[_Union[MigrationPayload.OtpParameters, _Mapping]]] = ..., version: _Optional[int] = ..., batch_size: _Optional[int] = ..., batch_index: _Optional[int] = ..., batch_id: _Optional[int] = ...) -> None: ...
