#!/usr/bin/env python3

"""CLI interface for pywifi using typer."""

import time
from typing import Annotated

import typer

from pywifi import const
from pywifi.iface import Interface
from pywifi.profile import Profile
from pywifi.wifi import PyWiFi

app = typer.Typer(help="pywifi - A cross-platform WiFi management tool")


def _get_interface(interface_index: int = 0) -> Interface:
    """Get WiFi interface by index."""
    wifi = PyWiFi()
    interfaces = wifi.interfaces()

    if not interfaces:
        typer.echo("Error: No WiFi interfaces found", err=True)
        raise typer.Exit(code=1)

    if interface_index >= len(interfaces):
        typer.echo(f"Error: Interface index {interface_index} not found", err=True)
        typer.echo(f"Available interfaces: 0-{len(interfaces) - 1}", err=True)
        raise typer.Exit(code=1)

    return interfaces[interface_index]


def _get_status_name(status: int) -> str:
    """Get human-readable status name."""
    status_names = {
        const.IFACE_DISCONNECTED: "DISCONNECTED",
        const.IFACE_SCANNING: "SCANNING",
        const.IFACE_INACTIVE: "INACTIVE",
        const.IFACE_CONNECTING: "CONNECTING",
        const.IFACE_CONNECTED: "CONNECTED",
    }
    return status_names.get(status, "UNKNOWN")


def _get_akm_name(akm: int) -> str:
    """Get human-readable AKM name."""
    akm_names = {
        const.AKM_TYPE_NONE: "NONE",
        const.AKM_TYPE_WPA: "WPA",
        const.AKM_TYPE_WPAPSK: "WPA-PSK",
        const.AKM_TYPE_WPA2: "WPA2",
        const.AKM_TYPE_WPA2PSK: "WPA2-PSK",
        const.AKM_TYPE_UNKNOWN: "UNKNOWN",
    }
    return akm_names.get(akm, "UNKNOWN")


@app.command()
def scan(
    interface: Annotated[
        int, typer.Option("--interface", "-i", help="WiFi interface index"),
    ] = 0,
    wait: Annotated[
        int, typer.Option("--wait", "-w", help="Seconds to wait for scan results"),
    ] = 5,
) -> None:
    """Scan for available WiFi networks."""
    iface = _get_interface(interface)

    typer.echo(f"Scanning on interface: {iface.name()}")
    iface.scan()

    typer.echo(f"Waiting {wait} seconds for scan results...")
    time.sleep(wait)

    results = iface.scan_results()

    if not results:
        typer.echo("No networks found")
        return

    typer.echo(f"\nFound {len(results)} network(s):\n")
    typer.echo(f"{'SSID':<32} {'BSSID':<18} {'Signal':<8} {'Security'}")
    typer.echo("-" * 80)

    for bss in results:
        ssid = bss.ssid if bss.ssid else "(Hidden)"
        bssid = bss.bssid if bss.bssid else "N/A"
        signal = str(bss.signal) if hasattr(bss, "signal") else "N/A"

        # Format security info
        security_parts = []
        if bss.akm:
            security_parts.extend([_get_akm_name(akm) for akm in bss.akm])
        security = ", ".join(security_parts) if security_parts else "Open"

        typer.echo(f"{ssid:<32} {bssid:<18} {signal:<8} {security}")


@app.command()
def connect(
    ssid: Annotated[str, typer.Argument(help="SSID of the network to connect to")],
    password: Annotated[
        str | None, typer.Option("--password", "-p", help="Network password"),
    ] = None,
    interface: Annotated[
        int, typer.Option("--interface", "-i", help="WiFi interface index"),
    ] = 0,
    timeout: Annotated[
        int, typer.Option("--timeout", "-t", help="Connection timeout in seconds"),
    ] = 10,
) -> None:
    """Connect to a WiFi network."""
    iface = _get_interface(interface)

    typer.echo(f"Connecting to '{ssid}' on interface: {iface.name()}")

    # Disconnect from current network
    iface.disconnect()
    time.sleep(1)

    # Create profile
    profile = Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN

    if password:
        # Assume WPA2-PSK for networks with password
        profile.akm = [const.AKM_TYPE_WPA2PSK]
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password
    else:
        # Open network
        profile.akm = [const.AKM_TYPE_NONE]

    # Add and connect to network
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)

    # Wait for connection
    typer.echo(f"Waiting for connection (timeout: {timeout}s)...")
    start_time = time.time()
    connected = False

    while time.time() - start_time < timeout:
        status = iface.status()
        if status == const.IFACE_CONNECTED:
            connected = True
            break
        time.sleep(1)

    if connected:
        typer.echo(f"Successfully connected to '{ssid}'")
    else:
        status = iface.status()
        status_name = _get_status_name(status)
        typer.echo(f"Failed to connect to '{ssid}'. Status: {status_name}", err=True)
        raise typer.Exit(code=1)


@app.command()
def disconnect(
    interface: Annotated[
        int, typer.Option("--interface", "-i", help="WiFi interface index"),
    ] = 0,
) -> None:
    """Disconnect from the current WiFi network."""
    iface = _get_interface(interface)

    typer.echo(f"Disconnecting interface: {iface.name()}")
    iface.disconnect()
    time.sleep(1)

    status = iface.status()
    if status in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:
        typer.echo("Successfully disconnected")
    else:
        status_name = _get_status_name(status)
        typer.echo(f"Disconnect may have failed. Status: {status_name}", err=True)


@app.command()
def status(
    interface: Annotated[
        int, typer.Option("--interface", "-i", help="WiFi interface index"),
    ] = 0,
) -> None:
    """Show the status of the WiFi interface."""
    iface = _get_interface(interface)

    typer.echo(f"Interface: {iface.name()}")
    status = iface.status()
    status_name = _get_status_name(status)
    typer.echo(f"Status: {status_name}")


@app.command()
def list_interfaces() -> None:
    """List all available WiFi interfaces."""
    wifi = PyWiFi()
    interfaces = wifi.interfaces()

    if not interfaces:
        typer.echo("No WiFi interfaces found")
        return

    typer.echo(f"Found {len(interfaces)} interface(s):\n")
    for idx, iface in enumerate(interfaces):
        status = iface.status()
        status_name = _get_status_name(status)
        typer.echo(f"  [{idx}] {iface.name()} - {status_name}")


if __name__ == "__main__":
    app()
