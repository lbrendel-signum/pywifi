#!/usr/bin/env python3

"""Implement Interface for manipulating wifi devies."""

import logging
import platform

from pywifi.profile import Profile

if platform.system().lower() == "windows":
    from . import _wifiutil_win as wifiutil
elif platform.system().lower() == "linux":
    from . import _wifiutil_linux as wifiutil
else:
    raise NotImplementedError


class Interface:
    """Interface provides methods for manipulating wifi devices."""

    """
    For encapsulating OS dependent behavior, we declare _raw_obj here for
    storing some common attribute (e.g. name) and os attributes (e.g. dbus
    objects for linux)
    """
    _raw_obj = {}
    _wifi_ctrl = {}
    _logger = None

    def __init__(self, raw_obj: dict[str]) -> None:
        """Create wifi interface instance"""
        self._raw_obj = raw_obj
        self._wifi_ctrl = wifiutil.WifiUtil()
        self._logger = logging.getLogger("pywifi")

    def name(self) -> str:
        """Get the name of the wifi interface."""
        return self._raw_obj["name"]

    def scan(self) -> None:
        """Trigger the wifi interface to scan."""
        self._logger.info("iface '%s' scans", self.name())
        self._wifi_ctrl.scan(self._raw_obj)

    def scan_results(self) -> list[Profile]:
        """Return the scan result."""
        bsses = self._wifi_ctrl.scan_results(self._raw_obj)

        if self._logger.isEnabledFor(logging.INFO):
            for bss in bsses:
                self._logger.info("Find bss:")
                self._logger.info("\tbssid: %s", bss.bssid)
                self._logger.info("\tssid: %s", bss.ssid)
                self._logger.info("\tfreq: %d", bss.freq)
                self._logger.info("\tauth: %s", bss.auth)
                self._logger.info("\takm: %s", bss.akm)
                self._logger.info("\tsignal: %d", bss.signal)

        return bsses

    def add_network_profile(self, params: Profile) -> Profile:
        """Add the info of the AP for connecting afterward."""
        return self._wifi_ctrl.add_network_profile(self._raw_obj, params)

    def remove_network_profile(self, params: Profile) -> None:
        """Remove the specified AP settings."""
        self._wifi_ctrl.remove_network_profile(self._raw_obj, params)

    def remove_all_network_profiles(self) -> None:
        """Remove all the AP settings."""
        self._wifi_ctrl.remove_all_network_profiles(self._raw_obj)

    def network_profiles(self) -> list[Profile]:
        """Get all the AP profiles."""
        profiles = self._wifi_ctrl.network_profiles(self._raw_obj)

        if self._logger.isEnabledFor(logging.INFO):
            for profile in profiles:
                self._logger.info("Get profile:")
                self._logger.info("\tssid: %s", profile.ssid)
                self._logger.info("\tauth: %s", profile.auth)
                self._logger.info("\takm: %s", profile.akm)
                self._logger.info("\tcipher: %s", profile.cipher)

        return profiles

    def connect(self, params: Profile) -> None:
        """Connect to the specified AP."""
        self._logger.info("iface '%s' connects to AP: '%s'", self.name(), params.ssid)
        self._wifi_ctrl.connect(self._raw_obj, params)

    def disconnect(self) -> None:
        """Disconnect from the specified AP."""
        self._logger.info("iface '%s' disconnects", self.name())
        self._wifi_ctrl.disconnect(self._raw_obj)

    def status(self) -> int:
        """Get the status of the wifi interface."""
        return self._wifi_ctrl.status(self._raw_obj)
