# **Network Information and Backup Script**
***
# Author: Christian Niessen
# Date: 2026-05-20
#

## **Overview**

This Python script automates the process of connecting to multiple Cisco IOS network devices via SSH, collecting diagnostic data, and creating configuration backups.
It is designed for network administrators who want quick and consistent access to device information for documentation, audits, or maintenance tasks.

Using a CSV file containing device IP addresses, the script logs in to each system, executes a series of `show` commands, and saves both the outputs and configuration backups into well-organized, timestamped directories.

***

## **Features**

- Interactive CSV file selection for flexible operation
- Secure credential input using Python’s `getpass()`
- Automatic creation of output folders based on timestamp
- Collection of key device data:
    - Running configuration*   
    - IOS version
    - Hardware inventory
    - CDP neighbor table
    - LLDP neighbor table
    - Routing table or default-gateway
    - Layer 3 interfaces
    - VLANs and interface statuses
- Error logging for authentication failures and unreachable hosts

* Anonymized version without the following values: username | password | secret | aaa | trustpoint | certificate

***

## **Directory Structure**

```
project_root/
│
├── csv_files/               # Input CSV files (device lists)
├── output/
│   └── <CSV_FILENAME>/
│       ├── dev-info/        # Text files with collected information
│       ├── dev-backup/      # Configuration backups
│       └── dev-error/       # Logs for connection/authentication errors
└── network_info_script.py   # The main Python script
```


***

## **Requirements**

Ensure the following Python module is installed:

```bash
pip install netmiko
```

Core system libraries used:

- `csv`
- `os`
- `sys`
- `datetime`
- `getpass`

***

## **CSV Input Format**

Each CSV file must include a header named `ip_add` containing IP addresses of target devices.

**Example:**

```csv
ip_add
192.168.10.1
192.168.10.2
10.1.1.5
```

All IPs in this list will be processed sequentially.

***

## **How It Works**

### **Step 1: File Selection**

At startup, the script scans the `csv_files/` directory for `.csv` files and displays them for selection:

```
Please select a file:
1: devices.csv
2: routers.csv
Enter number (or 'q' to quit):
```

You can type the number of the file or `q` to exit.

***

### **Step 2: Authentication**

After selecting a file, you’ll be prompted to enter credentials:

```
Please input user credentials
Username: admin
Password:
```

The password input is hidden for security.

***

### **Step 3: Directory Creation**

For each run, the script creates timestamped directories under `output/`, grouping:

- **`dev-info/`** for text-based device reports
- **`dev-backup/`** for full configuration backups
- **`dev-error/`** for connection and authentication logs

Example:

```
output/devices/dev-info/2025-06-04_14-30-21/
```


***

### **Step 4: Device Connection \& Command Execution**

Each IP from the CSV file is processed in sequence.
The script connects using `netmiko.ConnectHandler()` with device type `cisco_ios`.

Commands executed on each device:

```
show version | include Software
show inventory | section SN
show cdp neighbors
show lldp neighbors
show ip interface brief | exclude unassigned
show ip route vrf *
show running-config | include default-gateway
show vlan brief | include active
show interface status
```


***

### **Step 5: File Storage**

**Backup files** are saved under:

```
dev-backup/<hostname>_<ip>.cfg
```

**Device info reports** are saved under:

```
dev-info/<hostname>_<ip>.txt
```

Example content:

```
Hostname: SW-Core
MGMT-IP: 192.168.10.1
IOS-Version: Cisco IOS-XE Software, Version 17.9.4
Inventory:
PID: C9300-24T
CDP-Neighbors:
...
```


***

## **Error Handling**

If a device fails to authenticate or times out, the issue is logged.


| Error Type | Log File | Description |
| :-- | :-- | :-- |
| Authentication failure | `Auth_fail.txt` | Invalid credentials |
| Connection timeout | `Timeout.txt` | Unreachable or slow device |

Each log entry includes the affected IP address.

***

## **Example Console Output**

```
Please select a file:
1: devices.csv
Enter number (or 'q' to quit): 1
You selected: devices.csv
Please input user credentials
Username: admin
Password:
Connecting to 192.168.10.1 ...
Connection successful: SW-Core (192.168.10.1)
Backup successful: SW-Core (192.168.10.1)
Collection successful: SW-Core (192.168.10.1)
```

***

## **Example Error Output**

```
Connection timeout to 192.168.10.200
Authentication failed for 10.1.1.5
```

These messages also appear in the `output/.../dev-error/` folder.

***

## **Running the Script**

1. Place your CSV file in the `csv_files/` directory.
2. Run the script:

```bash
python3 network_info_script_2.1.py
```

3. Follow the prompts to select the file and enter credentials.
4. Output folders with timestamped results will appear in the `output/` directory.

***

## **License**

This script is intended for internal network administration and educational purposes.
No warranty is given for use in production environments — adjust commands and directories as needed.
