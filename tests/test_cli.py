#!/usr/bin/env python3

"""Test cases for pywifi CLI."""


from typer.testing import CliRunner

from pywifi.cli import app


def test_cli_help() -> None:
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "pywifi" in result.stdout
    assert "scan" in result.stdout
    assert "connect" in result.stdout
    assert "disconnect" in result.stdout


def test_cli_scan_help() -> None:
    """Test CLI scan help."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(app, ["scan", "--help"])

    assert result.exit_code == 0
    assert "Scan for available WiFi networks" in result.stdout
    assert "interface" in result.stdout
    assert "wait" in result.stdout


def test_cli_connect_help() -> None:
    """Test CLI connect help."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(app, ["connect", "--help"])

    assert result.exit_code == 0
    assert "Connect to a WiFi network" in result.stdout
    assert "SSID" in result.stdout or "ssid" in result.stdout
    assert "password" in result.stdout
    assert "interface" in result.stdout


def test_cli_disconnect_help() -> None:
    """Test CLI disconnect help."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(app, ["disconnect", "--help"])

    assert result.exit_code == 0
    assert "Disconnect" in result.stdout
    assert "interface" in result.stdout


def test_cli_status_help() -> None:
    """Test CLI status help."""
    runner = CliRunner()
    result = runner.invoke(app, ["status", "--help"])

    assert result.exit_code == 0
    assert "status" in result.stdout.lower()


def test_cli_list_interfaces_help() -> None:
    """Test CLI list-interfaces help."""
    runner = CliRunner()
    result = runner.invoke(app, ["list-interfaces", "--help"])

    assert result.exit_code == 0
    assert "interface" in result.stdout.lower()

