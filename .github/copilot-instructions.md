# GitHub Copilot Instructions for pywifi

## Project Overview

pywifi is a cross-platform Python module for manipulating wireless interfaces on Windows and Linux platforms. It provides a simple, unified API for WiFi operations including scanning, connecting, disconnecting, and managing network profiles.

## Architecture

### Platform-Specific Implementations

- **Linux**: Uses `wpa_supplicant` through Unix socket communication (`_wifiutil_linux.py`)
- **Windows**: Uses Native Wifi API through COM interfaces (`_wifiutil_win.py`)

### Core Components

1. **PyWiFi** (`wifi.py`): Main entry point for accessing WiFi interfaces
2. **Interface** (`iface.py`): Represents a WiFi interface with methods for scanning, connecting, etc.
3. **Profile** (`profile.py`): Represents WiFi network settings (SSID, authentication, encryption)
4. **Constants** (`const.py`): Defines status codes, authentication types, cipher types, etc.

## Coding Standards

### Style Guidelines

- Follow PEP 8 conventions
- Use Ruff for linting (configured in `pyproject.toml`)
- Line length: 100 characters max
- Use type hints for function parameters and return values
- Add docstrings for all public classes and methods

### Testing

- Tests are located in `tests/pywifi_test.py`
- Use pytest for running tests
- Mock external dependencies (OS calls, sockets) using the `pywifi_test_patch` decorator
- Test coverage should include basic operations: scan, connect, disconnect, status checks

### Platform Compatibility

- Support both Windows and Linux
- Use platform detection: `platform.system().lower()`
- Keep platform-specific code in separate utility modules
- Maintain consistent API across platforms

## Key Concepts

### Network Profile Structure

A Profile contains:
- `ssid`: Network name
- `auth`: Authentication algorithm (typically `AUTH_ALG_OPEN`)
- `akm`: Key management type (list, e.g., `AKM_TYPE_WPA2PSK`)
- `cipher`: Cipher type (e.g., `CIPHER_TYPE_CCMP`)
- `key`: Network password (optional, required for encrypted networks)

### Interface States

- `IFACE_DISCONNECTED`: Not connected to any network
- `IFACE_SCANNING`: Currently scanning for networks
- `IFACE_INACTIVE`: Interface is inactive
- `IFACE_CONNECTING`: In process of connecting
- `IFACE_CONNECTED`: Successfully connected

### Typical Usage Flow

1. Create PyWiFi instance
2. Get interface (usually index 0)
3. Disconnect from current network (if any)
4. Create Profile with network details
5. Add network profile to interface
6. Connect using the profile
7. Check status to verify connection

## Best Practices

### Error Handling

- Log important operations using the logger
- Check interface status before performing operations
- Handle platform-specific errors gracefully
- Provide meaningful error messages

### Security

- Don't log sensitive data (passwords, keys)
- Use secure communication with wpa_supplicant
- Validate input parameters (SSID length, key format)

### Performance

- Allow sufficient time for scanning (2-8 seconds)
- Add delays after connect/disconnect operations
- Don't spam status checks - allow operations to complete

### Documentation

- Keep README.md and DOC.md in sync with code changes
- Document all public APIs
- Provide code examples for common use cases
- Note platform-specific behavior

## Development Workflow

1. **Setup**: Install dependencies with `pip install .` or use uv
2. **Testing**: Run `pytest tests/` to execute test suite
3. **Linting**: Use `ruff check .` to check code style
4. **Platform Testing**: Test on both Windows and Linux when possible

## Common Patterns

### Adding a New Feature

1. Update platform-specific utility files if needed
2. Modify `iface.py` to expose the feature
3. Add corresponding tests in `pywifi_test.py`
4. Update documentation in DOC.md
5. Consider backward compatibility

### Debugging

- Enable logging to see detailed operation flow
- Check wpa_supplicant on Linux: `wpa_cli status`
- Verify socket communication is working
- Use mocks in tests to isolate issues

## Important Notes

- The project uses both `setup.py` and `pyproject.toml` for configuration
- Minimum Python version: 3.10 (per pyproject.toml)
- Dependencies: `comtypes` for Windows COM interface access
- The project is licensed under MIT License

## References

- [Documentation](DOC.md): Detailed API documentation
- [README](README.md): Installation and usage examples
- [wpa_supplicant](https://w1.fi/wpa_supplicant/): Linux WiFi management
- [Native Wifi API](https://msdn.microsoft.com/en-us/library/windows/desktop/ms706556.aspx): Windows WiFi API
