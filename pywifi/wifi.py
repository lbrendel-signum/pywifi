#!/usr/bin/env python3

"""wifi - entry module of pywifi libary.

We put the fundamental implementation of wifi functions in each OS
folder (e.g. linux, win, and osx). So, PyWiFi class is just the
entry point to manipulate wifi devices.
"""

import logging
import platform

from pywifi.iface import Interface

if platform.system().lower() == "windows":
    from pywifi import _wifiutil_win as wifiutil
elif platform.system().lower() == "linux":
    from pywifi import _wifiutil_linux as wifiutil
else:
    raise NotImplementedError


class PyWiFi:
    """PyWiFi provides operations to manipulate wifi devices."""

    _ifaces = []
    _logger = None

    def __init__(self) -> None:
        """Create PyWiFi instance"""
        self._logger = logging.getLogger("pywifi")

    def interfaces(self) -> list[Interface]:
        """Collect the available wlan interfaces."""
        self._ifaces = []
        wifi_ctrl = wifiutil.WifiUtil()

        for interface in wifi_ctrl.interfaces():
            iface = Interface(interface)
            self._ifaces.append(iface)
            self._logger.info("Get interface: %s", iface.name())

        if not self._ifaces:
            self._logger.error("Can't get wifi interface")

        return self._ifaces
