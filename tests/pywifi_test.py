#!/usr/bin/env python3

"""Test cases for pywifi."""

# For mocking
import os
import platform
import socket
import stat
import time
from typing import Any

import pywifi
from pywifi import const


class SockMock:
    default_scan_results = (
        "bssid / frequency / signal level / flags / ssid\n"
        "14:4d:67:14:1e:44\t2412\t-67\t[WPA2-PSK-CCMP][WPS][ESS]\tTOTOLINK N302RE\n"
        "ac:9e:17:31:85:fc\t2437\t-63\t[WPA2-PSK-CCMP][WPS][ESS]\tEvan\n"
        "0c:80:63:2b:0d:a8\t2417\t-79\t[WPA2-PSK-CCMP][WPS][ESS]\tKevin_H2\n"
        "78:32:1b:63:96:05\t2422\t-91\t[WPA-PSK-CCMP][WPA2-PSK-CCMP][ESS]\tjoyfulness\n"
    )

    def __init__(self):
        self._last_cmd = None
        self._last_state = None
        self._network_profiles = []

    def bind(self, *args, **kwargs) -> None:
        pass

    def connect(self, *args, **kwargs) -> None:
        pass

    def recv(self, *args, **kwargs) -> None:
        if self._last_cmd == "SCAN":

            return b"OK\n"
        if self._last_cmd == "PING":

            return b"PONG"
        if self._last_cmd == "SCAN_RESULTS":

            return bytearray(self.default_scan_results, "utf-8")
        if self._last_cmd == "DISCONNECT":

            self._last_state = 0

            return b"OK\n"
        if self._last_cmd[0 : len("SELECT_NETWORK")] == "SELECT_NETWORK":

            self._last_state = 1

            return b"OK\n"
        if self._last_cmd == "STATUS":

            if self._last_state == 0:
                status = "wpa_state=DISCONNECTED"
            elif self._last_state == 1:
                status = "wpa_state=COMPLETED"

            return bytearray(status, "utf-8")
        if self._last_cmd == "REMOVE_NETWORK all":

            self._network_profiles = self._network_profiles[:]

            return b"OK\n"
        if self._last_cmd[: len("REMOVE_NETWORK")] == "REMOVE_NETWORK":

            network_id = int(self._last_cmd.split(" ")[1])

            for idx, network in enumerate(self._network_profiles):
                if network["id"] == network_id:
                    del self._network_profiles[idx]
                    break

            return b"OK\n"
        if self._last_cmd == "LIST_NETWORKS":

            networks = "network id / ssid / bssid / flag\n"

            for network in self._network_profiles:
                networks += "{}\t{}\t{}\t[DISABLED]\n".format(
                    network["id"], network["ssid"], network.get("bssid", "None")
                )

            return bytearray(networks, "utf-8")
        if self._last_cmd == "ADD_NETWORK":
            if self._network_profiles:
                self._network_profiles.sort(key=lambda obj: obj["id"])
                network_id = self._network_profiles[-1]["id"] + 1
            else:
                network_id = 0

            network = {}
            network["id"] = network_id
            self._network_profiles.append(network)

            return bytearray(str(network_id), "utf-8")
        if self._last_cmd[: len("SET_NETWORK")] == "SET_NETWORK":
            network_id = int(self._last_cmd.split(" ")[1])
            field_name = self._last_cmd.split(" ")[2]
            val = self._last_cmd.split(" ")[3]

            for profile in self._network_profiles:
                if profile["id"] == network_id:
                    network = profile

            if field_name == "ssid":
                val = val[1:-1]

            network[field_name] = val

            return b"OK\n"
        if self._last_cmd[: len("GET_NETWORK")] == "GET_NETWORK":
            network_id = int(self._last_cmd.split(" ")[1])
            field_name = self._last_cmd.split(" ")[2]

            for profile in self._network_profiles:
                if profile["id"] == network_id:
                    network = profile

            if field_name == "pairwise":
                val = "CCMP TKIP"
            elif field_name == "ssid":
                val = '"' + network[field_name] + '"'
            else:
                val = network[field_name]

            return bytearray(val, "utf-8")
        return None

    def send(self, *args, **kwargs):
        self._last_cmd = args[0].decode("utf-8")


class Mock:
    """Mock class"""

    def __init__(self) -> None:
        self._dict = {}
        # Add default attributes that os.stat should return
        self._dict["st_mode"] = 0o140000  # Socket file mode

    def __getattr__(self, field: str) -> Any:  # noqa: ANN401
        return self._dict.get(field, None)


def pywifi_test_patch(test_func) -> None:
    def core_patch(*args, **kwargs):
        # Save original functions
        original_stat = os.stat
        original_listdir = os.listdir
        original_S_ISSOCK = stat.S_ISSOCK
        original_socket = socket.socket
        original_remove = os.remove
        
        # Create mocks that accept both args and kwargs
        os.stat = lambda *_args, **_kwargs: Mock()
        os.listdir = lambda *_args, **_kwargs: ["wlx000c433243ce"]
        stat.S_ISSOCK = lambda *_args, **_kwargs: True
        socket.socket = lambda *_args, **_kwargs: SockMock()
        os.remove = lambda *_args, **_kwargs: True

        try:
            test_func(*args, **kwargs)
        finally:
            # Restore original functions
            os.stat = original_stat
            os.listdir = original_listdir
            stat.S_ISSOCK = original_S_ISSOCK
            socket.socket = original_socket
            os.remove = original_remove

    return core_patch


@pywifi_test_patch
def test_interfaces() -> None:
    wifi = pywifi.PyWiFi()

    assert wifi.interfaces()

    if platform.system().lower() == "windows":
        assert wifi.interfaces()[0].name() == "Intel(R) Dual Band Wireless-AC 7260"
    elif platform.system().lower() == "linux":
        assert wifi.interfaces()[0].name() == "wlx000c433243ce"


@pywifi_test_patch
def test_scan() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(5)
    bsses = iface.scan_results()
    assert bsses


def test_profile_comparison() -> None:
    profile1 = pywifi.Profile()
    profile1.ssid = "testap"
    profile1.auth = const.AUTH_ALG_OPEN
    profile1.akm.append(const.AKM_TYPE_WPA2PSK)
    profile1.cipher = const.CIPHER_TYPE_CCMP
    profile1.key = "12345678"

    profile2 = pywifi.Profile()
    profile2.ssid = "testap"
    profile2.auth = const.AUTH_ALG_OPEN
    profile2.akm.append(const.AKM_TYPE_WPA2PSK)
    profile2.cipher = const.CIPHER_TYPE_CCMP
    profile2.key = "12345678"

    assert profile1 == profile2

    profile3 = pywifi.Profile()
    profile3.ssid = "testap"
    profile3.auth = const.AUTH_ALG_OPEN
    profile3.akm.append(const.AKM_TYPE_WPAPSK)
    profile3.cipher = const.CIPHER_TYPE_CCMP
    profile3.key = "12345678"

    assert profile1 == profile3


@pywifi_test_patch
def test_add_network_profile() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]

    profile = pywifi.Profile()
    profile.ssid = "testap"
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = "12345678"

    iface.remove_all_network_profiles()

    assert len(iface.network_profiles()) == 0

    iface.add_network_profile(profile)
    profiles = iface.network_profiles()

    assert profiles is not None
    assert profiles[0].ssid == "testap"
    assert const.AKM_TYPE_WPA2PSK in profiles[0].akm
    assert profiles[0].auth == const.AUTH_ALG_OPEN


@pywifi_test_patch
def test_remove_network_profile() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]
    iface.remove_all_network_profiles()

    assert len(iface.network_profiles()) == 0

    profile1 = pywifi.Profile()
    profile1.ssid = "testap"
    profile1.auth = const.AUTH_ALG_OPEN
    profile1.akm.append(const.AKM_TYPE_WPA2PSK)
    profile1.cipher = const.CIPHER_TYPE_CCMP
    profile1.key = "12345678"
    iface.add_network_profile(profile1)

    profile2 = pywifi.Profile()
    profile2.ssid = "testap2"
    profile2.auth = const.AUTH_ALG_OPEN
    profile2.akm.append(const.AKM_TYPE_WPA2PSK)
    profile2.cipher = const.CIPHER_TYPE_CCMP
    profile2.key = "12345678"
    iface.add_network_profile(profile2)

    profile3 = pywifi.Profile()
    profile3.ssid = "testap3"
    profile3.auth = const.AUTH_ALG_OPEN
    profile3.akm.append(const.AKM_TYPE_WPAPSK)
    profile3.cipher = const.CIPHER_TYPE_TKIP
    profile3.key = "12345678"
    iface.add_network_profile(profile3)

    profiles = iface.network_profiles()

    assert len(profiles) == 3

    iface.remove_network_profile(profile2)

    profiles = iface.network_profiles()

    assert len(profiles) == 2
    assert profile2 not in profiles


@pywifi_test_patch
def test_status() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]
    iface.disconnect()
    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]


@pywifi_test_patch
def test_connect() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]

    iface.disconnect()
    time.sleep(1)
    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]

    profile = pywifi.Profile()
    profile.ssid = "testap"
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = "12345678"

    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)

    iface.connect(tmp_profile)
    time.sleep(5)
    assert iface.status() == const.IFACE_CONNECTED

    iface.disconnect()
    time.sleep(1)
    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]


@pywifi_test_patch
def test_connect_open() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]

    iface.disconnect()
    time.sleep(1)
    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]

    profile = pywifi.Profile()
    profile.ssid = "testap"
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_NONE)

    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)

    iface.connect(tmp_profile)
    time.sleep(5)
    assert iface.status() == const.IFACE_CONNECTED

    iface.disconnect()
    time.sleep(1)
    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]


@pywifi_test_patch
def test_disconnect() -> None:
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]
    iface.disconnect()

    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]
