#!/usr/bin/env python3

"""Constants used in pywifi library define here."""

from enum import IntEnum


class IfaceStatus(IntEnum):
    """Interface status constants."""

    DISCONNECTED = 0
    SCANNING = 1
    INACTIVE = 2
    CONNECTING = 3
    CONNECTED = 4


class AuthAlgorithm(IntEnum):
    """Authentication algorithm constants."""

    OPEN = 0
    SHARED = 1


class AkmType(IntEnum):
    """Authentication key management type constants."""

    NONE = 0
    WPA = 1
    WPAPSK = 2
    WPA2 = 3
    WPA2PSK = 4
    UNKNOWN = 5


class CipherType(IntEnum):
    """Cipher type constants."""

    NONE = 0
    WEP = 1
    TKIP = 2
    CCMP = 3
    UNKNOWN = 4


class KeyType(IntEnum):
    """Key type constants."""

    NETWORKKEY = 0
    PASSPHRASE = 1


# Backward compatibility - keep old constant names as aliases
IFACE_DISCONNECTED = IfaceStatus.DISCONNECTED
IFACE_SCANNING = IfaceStatus.SCANNING
IFACE_INACTIVE = IfaceStatus.INACTIVE
IFACE_CONNECTING = IfaceStatus.CONNECTING
IFACE_CONNECTED = IfaceStatus.CONNECTED

AUTH_ALG_OPEN = AuthAlgorithm.OPEN
AUTH_ALG_SHARED = AuthAlgorithm.SHARED

AKM_TYPE_NONE = AkmType.NONE
AKM_TYPE_WPA = AkmType.WPA
AKM_TYPE_WPAPSK = AkmType.WPAPSK
AKM_TYPE_WPA2 = AkmType.WPA2
AKM_TYPE_WPA2PSK = AkmType.WPA2PSK
AKM_TYPE_UNKNOWN = AkmType.UNKNOWN

CIPHER_TYPE_NONE = CipherType.NONE
CIPHER_TYPE_WEP = CipherType.WEP
CIPHER_TYPE_TKIP = CipherType.TKIP
CIPHER_TYPE_CCMP = CipherType.CCMP
CIPHER_TYPE_UNKNOWN = CipherType.UNKNOWN

KEY_TYPE_NETWORKKEY = KeyType.NETWORKKEY
KEY_TYPE_PASSPHRASE = KeyType.PASSPHRASE
