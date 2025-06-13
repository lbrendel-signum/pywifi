#!/usr/bin/env python3

"""Define WiFi Profile."""

from pywifi.const import AKM_TYPE_NONE, AUTH_ALG_OPEN, CIPHER_TYPE_NONE


class Profile:
    """Definition of a Wifi profile"""

    def __init__(self) -> None:
        """Create instance of a wifi profile"""
        self.id = 0
        self.auth: int = AUTH_ALG_OPEN
        self.akm: list[int] = [AKM_TYPE_NONE]
        self.cipher: int = CIPHER_TYPE_NONE
        self.ssid: str = None
        self.bssid: str = None
        self.key: str = None

    def process_akm(self) -> None:
        if len(self.akm) > 1:
            self.akm = self.akm[-1:]

    def __eq__(self, profile: "Profile") -> bool:
        """Check if two Profile instances are the same"""
        if profile.ssid and profile.ssid != self.ssid:
            return False

        if profile.bssid and profile.bssid != self.bssid:
            return False

        if profile.auth and profile.auth != self.auth:
            return False

        if profile.cipher and profile.cipher != self.cipher:
            return False

        return not (profile.akm and set(profile.akm).isdisjoint(set(self.akm)))
