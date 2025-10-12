
# Documentation

## CLI Usage

pywifi includes a command-line interface for easy WiFi management from the terminal.

### Basic Commands

#### List Interfaces

List all available WiFi interfaces on your system:

```bash
pywifi list-interfaces
```

#### Scan for Networks

Scan for available WiFi networks:

```bash
pywifi scan
```

Options:
- `--interface/-i`: WiFi interface index (default: 0)
- `--wait/-w`: Seconds to wait for scan results (default: 5)

Example:
```bash
pywifi scan --wait 10 --interface 0
```

#### Connect to Network

Connect to a WiFi network:

```bash
# Connect to an open network
pywifi connect "Network-SSID"

# Connect to a secured network (WPA2-PSK)
pywifi connect "Network-SSID" --password "your-password"
```

Options:
- `--password/-p`: Network password (for secured networks)
- `--interface/-i`: WiFi interface index (default: 0)
- `--timeout/-t`: Connection timeout in seconds (default: 10)

Example:
```bash
pywifi connect "MyHomeWiFi" -p "MyPassword123" -t 15
```

#### Disconnect from Network

Disconnect from the current WiFi network:

```bash
pywifi disconnect
```

Options:
- `--interface/-i`: WiFi interface index (default: 0)

#### Check Status

Check the status of a WiFi interface:

```bash
pywifi status
```

Options:
- `--interface/-i`: WiFi interface index (default: 0)

### Getting Help

Get help for any command:

```bash
pywifi --help
pywifi scan --help
pywifi connect --help
pywifi disconnect --help
pywifi status --help
pywifi list-interfaces --help
```

## Constants

Following constatns are defined in pywifi.

Before using the constants, please remember to ```import pywifi```.

### Interface Status

```Interface.status()``` will return one of the status code below.

```
const.IFACE_DISCONNECTED
const.IFACE_SCANNING
const.IFACE_INACTIVE
const.IFACE_CONNECTING
const.IFACE_CONNECTED
```

### Authentication Algorithms

Authentication algorithm should be assined to a *Profile*.
For normal case, almost all the APs use *open* algorithm.

```
const.AUTH_OPEN
const.AUTH_SHARED
```

### Key Management Type

The key management type should be assigned to a *Profile*.

For normal APs, if
- an AP is no security setting, set the profile akm as ```AKM_TYPE_NONE```.
- an AP is in WPA mode, set the profile akm as ```AKM_TYUPE_WPAPSK```.
- an AP is in WPA2 mode, set the profile akm as ```AKM_TYUPE_WPA2PSK```.

```AKM_TYPE_WPA``` and ```AKM_TYPE_WPA2``` are used by the enterprise APs.

```
const.AKM_TYPE_NONE
const.AKM_TYPE_WPA
const.AKM_TYPE_WPAPSK
const.AKM_TYPE_WPA2
const.AKM_TYPE_WPA2PSK
```

### Cipher Types

The cipher type should be set to the *Profile* if the akm is not ```AKM_TYPE_NONE```.
You can refer to the setting of the AP you want to connect to.

```
const.CIPHER_TYPE_NONE
const.CIPHER_TYPE_WEP
const.CIPHER_TYPE_TKIP
const.CIPHER_TYPE_CCMP
```

## Network Profile

A **Profile** is the settings of the AP we want to connect to.
The fields of an profile:

- ```ssid``` - The ssid of the AP.
- ```auth``` - The authentication algorithm of the AP.
- ```akm``` - The key management type of the AP.
- ```cipher``` - The cipher type of the AP.
- ```key``` *(optinoal)* - The key of the AP.
This should be set if the cipher is not ```CIPHER_TYPE_NONE```.

Example:

```
import pywifi

profile = pywifi.Profile()
profile.ssid = 'testap'
profile.auth = const.AUTH_ALG_OPEN
profile.akm.append(const.AKM_TYPE_WPA2PSK)
profile.cipher = const.CIPHER_TYPE_CCMP
profile.key = '12345678'

wifi = pywifi.PyWiFi()
iface = wifi.interfaces()[0]
profile = iface.add_network_profile(profile)
iface.connect(profile)
```

## Interface

An **Interface** means the Wi-Fi interface which we use to perform
Wi-Fi operations (e.g. scan, connect, disconnect, ...).

### Get interface information

In general, there will be only one Wi-Fi interface in the platform.
Thus, use index *0* to obtain the Wi-Fi interface.

```
import pywifi

wifi = pywifi.PyWiFi()
iface = wifi.interfaces()[0]
```

### Interface.name()

Get the name of the Wi-Fi interface.

### Interface.scan()

Trigger the interface to scan APs.

### Interface.scan_results()

Obtain the results of the previous triggerred scan.
A **Profile** list will be returned.

*Note.* Because the scan time for each Wi-Fi interface is variant.
It is safer to call ```scan_results()``` 2 ~ 8 seconds later after
calling ```scan()```.

### Interface.add_network_profile(*profile*)

Add the AP profile for connecting to later.

### Interface.remove_all_network_profiles()

Remove all the AP profiles.

### Interface.network_profiles()

Obtain all the saved AP profiles by returning a **Profile** list.

### Interface.connect(*profile*)

Connect to the specified AP by the given *profile*.
*Note.* As current design, ```add_network_profile(profile)``` should be
called before ```connect(profile)``` is called.

### Interface.disconnect()

Disconnect current AP connection.

### Interface.status()

Get the status of current status.

(C) Jiang Sheng-Jhih 2017, [MIT License].
