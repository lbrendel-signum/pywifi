#!/usr/bin/env python3

"""Implementations of wifi functions of Linux."""

import logging
import os
import socket
import stat

from pywifi.const import (
    AkmType,
    AuthAlgorithm,
    CipherType,
    IfaceStatus,
)
from pywifi.profile import Profile

CTRL_IFACE_DIR = "/var/run/wpa_supplicant"
CTRL_IFACE_RETRY = 3
REPLY_SIZE = 4096

status_dict = {
    "completed": IfaceStatus.CONNECTED,
    "inactive": IfaceStatus.INACTIVE,
    "authenticating": IfaceStatus.CONNECTING,
    "associating": IfaceStatus.CONNECTING,
    "associated": IfaceStatus.CONNECTING,
    "4way_handshake": IfaceStatus.CONNECTING,
    "group_handshake": IfaceStatus.CONNECTING,
    "interface_disabled": IfaceStatus.INACTIVE,
    "disconnected": IfaceStatus.DISCONNECTED,
    "scanning": IfaceStatus.SCANNING,
}

key_mgmt_to_str = {
    AkmType.WPA: "WPA-EAP",
    AkmType.WPAPSK: "WPA-PSK",
    AkmType.WPA2: "WPA-EAP",
    AkmType.WPA2PSK: "WPA-PSK",
}

key_mgmt_to_proto_str = {
    AkmType.WPA: "WPA",
    AkmType.WPAPSK: "WPA",
    AkmType.WPA2: "RSN",
    AkmType.WPA2PSK: "RSN",
}

proto_to_key_mgmt_id = {"WPA": AkmType.WPAPSK, "RSN": AkmType.WPA2PSK}

cipher_str_to_value = {
    "TKIP": CipherType.TKIP,
    "CCMP": CipherType.CCMP,
}


class WifiUtil:
    """WifiUtil implements the wifi functions in Linux."""

    _connections = {}
    _logger = logging.getLogger("pywifi")

    def scan(self, obj: dict[str, str]) -> None:
        """Trigger the wifi interface to scan."""
        self._send_cmd_to_wpas(obj["name"], "SCAN")

    def scan_results(self, obj: dict[str, str]) -> list[Profile]:
        """Get the AP list after scanning."""
        bsses = []
        bsses_summary: list[str] = self._send_cmd_to_wpas(
            obj["name"], "SCAN_RESULTS", get_reply=True
        )
        bsses_summary = bsses_summary[:-1].split("\n")
        if len(bsses_summary) == 1:
            return bsses

        for item in bsses_summary[1:]:
            values = item.split("\t")
            bss = Profile()
            bss.bssid = values[0]
            bss.freq = int(values[1])
            bss.signal = int(values[2])
            bss.ssid = values[4]
            bss.akm = []
            if "WPA-PSK" in values[3]:
                bss.akm.append(AkmType.WPAPSK)
            if "WPA2-PSK" in values[3]:
                bss.akm.append(AkmType.WPA2PSK)
            if "WPA-EAP" in values[3]:
                bss.akm.append(AkmType.WPA)
            if "WPA2-EAP" in values[3]:
                bss.akm.append(AkmType.WPA2)

            bss.auth = AuthAlgorithm.OPEN

            bsses.append(bss)

        return bsses

    def connect(self, obj: dict[str, str], network: Profile) -> None:
        """Connect to the specified AP."""
        network_summary = self._send_cmd_to_wpas(obj["name"], "LIST_NETWORKS", get_reply=True)
        network_summary = network_summary[:-1].split("\n")
        if len(network_summary) == 1:
            return

        for item in network_summary[1:]:
            values = item.split("\t")
            if values[1] == network.ssid:
                network_summary = self._send_cmd_to_wpas(
                    obj["name"],
                    f"SELECT_NETWORK {values[0]}",
                    get_reply=True,
                )

    def disconnect(self, obj: dict[str, str]) -> None:
        """Disconnect to the specified AP."""
        self._send_cmd_to_wpas(obj["name"], "DISCONNECT")

    def add_network_profile(self, obj: dict[str, str], params: Profile) -> Profile:
        """Add an AP profile for connecting to afterward."""
        network_id = self._send_cmd_to_wpas(obj["name"], "ADD_NETWORK", get_reply=True)
        network_id = network_id.strip()

        params.process_akm()

        self._send_cmd_to_wpas(
            obj["name"],
            f'SET_NETWORK {network_id} ssid "{params.ssid}"',
        )

        key_mgmt = ""
        if params.akm[-1] in [AkmType.WPAPSK, AkmType.WPA2PSK]:
            key_mgmt = "WPA-PSK"
        elif params.akm[-1] in [AkmType.WPA, AkmType.WPA2]:
            key_mgmt = "WPA-EAP"
        else:
            key_mgmt = "NONE"

        if key_mgmt:
            self._send_cmd_to_wpas(
                obj["name"],
                f"SET_NETWORK {network_id} key_mgmt {key_mgmt}",
            )

        proto = ""
        if params.akm[-1] in [AkmType.WPAPSK, AkmType.WPA]:
            proto = "WPA"
        elif params.akm[-1] in [AkmType.WPA2PSK, AkmType.WPA2]:
            proto = "RSN"

        if proto:
            self._send_cmd_to_wpas(
                obj["name"],
                f"SET_NETWORK {network_id} proto {proto}",
            )

        if params.akm[-1] in [AkmType.WPAPSK, AkmType.WPA2PSK]:
            self._send_cmd_to_wpas(
                obj["name"],
                f'SET_NETWORK {network_id} psk "{params.key}"',
            )

        return params

    def network_profiles(self, obj: dict[str, str]) -> list[Profile]:
        """Get AP profiles."""
        networks = []
        network_ids = []
        network_summary = self._send_cmd_to_wpas(obj["name"], "LIST_NETWORKS", get_reply=True)
        network_summary = network_summary[:-1].split("\n")
        if len(network_summary) == 1:
            return networks

        for item in network_summary[1:]:
            network_ids.append(item.split()[0])

        for network_id in network_ids:
            network = Profile()

            network.id = network_id

            ssid = self._send_cmd_to_wpas(
                obj["name"],
                f"GET_NETWORK {network_id} ssid",
                get_reply=True,
            )
            if ssid.upper().startswith("FAIL"):
                continue
            network.ssid = ssid[1:-1]

            key_mgmt = self._send_cmd_to_wpas(
                obj["name"],
                f"GET_NETWORK {network_id} key_mgmt",
                get_reply=True,
            )

            network.akm = []
            if key_mgmt.upper().startswith("FAIL"):
                continue
            if key_mgmt.upper() in ["WPA-PSK"]:
                proto = self._send_cmd_to_wpas(
                    obj["name"],
                    f"GET_NETWORK {network_id} proto",
                    get_reply=True,
                )

                if proto.upper() == "RSN":
                    network.akm.append(AkmType.WPA2PSK)
                else:
                    network.akm.append(AkmType.WPAPSK)
            elif key_mgmt.upper() in ["WPA-EAP"]:
                proto = self._send_cmd_to_wpas(
                    obj["name"],
                    f"GET_NETWORK {network_id} proto",
                    get_reply=True,
                )

                if proto.upper() == "RSN":
                    network.akm.append(AkmType.WPA2)
                else:
                    network.akm.append(AkmType.WPA)

            ciphers = self._send_cmd_to_wpas(
                obj["name"],
                f"GET_NETWORK {network_id} pairwise",
                get_reply=True,
            ).split(" ")

            if ciphers[0].upper().startswith("FAIL"):
                continue
            # Assume the possible ciphers TKIP and CCMP
            if len(ciphers) == 1:
                network.cipher = cipher_str_to_value(ciphers[0].upper())
            elif "CCMP" in ciphers:
                network.cipher = CipherType.CCMP

            networks.append(network)

        return networks

    def remove_network_profile(self, obj: dict[str, str], params: Profile) -> None:
        """Remove the specified AP profiles"""
        network_id = -1
        profiles = self.network_profiles(obj)

        for profile in profiles:
            if profile == params:
                network_id = profile.id

        if network_id != -1:
            self._send_cmd_to_wpas(obj["name"], f"REMOVE_NETWORK {network_id}")

    def remove_all_network_profiles(self, obj: dict[str, str]) -> None:
        """Remove all the AP profiles."""
        self._send_cmd_to_wpas(obj["name"], "REMOVE_NETWORK all")

    def status(self, obj: dict[str, str]) -> int:
        """Get the wifi interface status."""
        reply = self._send_cmd_to_wpas(obj["name"], "STATUS", get_reply=True)
        result = reply.split("\n")

        status = ""
        for item in result:
            if item.startswith("wpa_state="):
                status = item[10:]
                return status_dict[status.lower()]
        return IfaceStatus.DISCONNECTED

    def interfaces(self) -> list[dict[str, str]]:
        """Get the wifi interface lists."""
        ifaces = []
        for f in sorted(os.listdir(CTRL_IFACE_DIR)):
            sock_file = f"{CTRL_IFACE_DIR}/{f}"
            mode = os.stat(sock_file).st_mode
            if stat.S_ISSOCK(mode):
                iface = {}
                iface["name"] = f
                ifaces.append(iface)
                self._connect_to_wpa_s(f)

        return ifaces

    def _connect_to_wpa_s(self, iface: str) -> None:
        ctrl_iface = "/".join([CTRL_IFACE_DIR, iface])
        if ctrl_iface in self._connections:
            self._logger.info("Connection for iface '%s' aleady existed!", iface)

        sock_file = "{}/{}_{}".format("/tmp", "pywifi", iface)
        self._remove_existed_sock(sock_file)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.bind(sock_file)
        sock.connect(ctrl_iface)

        send_len = sock.send(b"PING")
        retry = CTRL_IFACE_RETRY
        while retry >= 0:
            reply = sock.recv(REPLY_SIZE)
            if reply == b"":
                self._logger.error("Connection to '%s' is broken!", ctrl_iface)
                break

            if reply.startswith(b"PONG"):
                self._logger.info("Connect to sock '%s' successfully!", ctrl_iface)
                self._connections[iface] = {
                    "sock": sock,
                    "sock_file": sock_file,
                    "ctrl_iface": ctrl_iface,
                }
                break
            retry -= 1

    def _remove_existed_sock(self, sock_file: str) -> None:
        if os.path.exists(sock_file):
            mode = os.stat(sock_file).st_mode
            if stat.S_ISSOCK(mode):
                os.remove(sock_file)

    def _send_cmd_to_wpas(self, iface: str, cmd: str, *, get_reply: bool = False) -> str | None:
        if "psk" not in cmd:
            self._logger.info("Send cmd '%s' to wpa_s", cmd)
        sock = self._connections[iface]["sock"]

        sock.send(bytearray(cmd, "utf-8"))
        reply = sock.recv(REPLY_SIZE)
        if get_reply:
            return reply.decode("utf-8")

        if reply != b"OK\n":
            self._logger.error(
                "Unexpected resp '%s' for Command '%s'",
                reply.decode("utf-8"),
                cmd,
            )
        return None
