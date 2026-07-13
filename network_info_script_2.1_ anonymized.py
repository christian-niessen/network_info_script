#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Script for network information tasks
# Author: Christian Niessen
# Date: 2026-05-20
#

import csv
import sys
import os
from datetime import datetime
from getpass import getpass
from netmiko import ConnectHandler, exceptions

script_dir = os.path.dirname(os.path.abspath(__file__))

directory = os.path.join(script_dir, "csv_files")

if not os.path.isdir(directory):
    print(f"Directory not found: {directory}")
    sys.exit(1)

csv_files = sorted([file for file in os.listdir(directory) if file.endswith('.csv')])

if not csv_files:
    print("No CSV files found.")
    sys.exit(1)

print("Please select a file:")
for idx, file in enumerate(csv_files, 1):
    print(f"{idx}: {file}")

selected_file = None
while selected_file is None:
    selection = input("Enter number (or 'q' to quit): ")
    if selection.lower() == 'q':
        print("Exiting.")
        sys.exit(0)
    try:
        selection_idx = int(selection) - 1
        if 0 <= selection_idx < len(csv_files):
            selected_file = csv_files[selection_idx]
            print(f"You selected: {selected_file}")
        else:
            print("Invalid selection. Please try again.")
    except ValueError:
        print("Please enter a valid number.")

print("Please input user credentials")
username = input("Username:")
password = getpass("Password:")

now = datetime.now()
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
selected_file_no_ext = os.path.splitext(selected_file)[0]

info_dir = os.path.join(script_dir, "output", selected_file_no_ext, "dev-info", timestamp)
os.makedirs(info_dir, exist_ok=True)

backup_dir = os.path.join(script_dir, "output", selected_file_no_ext, "dev-backup", timestamp)
os.makedirs(backup_dir, exist_ok=True)

error_dir = os.path.join(script_dir, "output", selected_file_no_ext, "dev-error", timestamp) 
os.makedirs(error_dir, exist_ok=True)

def main():

    ip_address = []
    csv_filepath = os.path.join(directory, selected_file)
    with open(csv_filepath, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            if 'ip_add' in row and row['ip_add'].strip():
                ip_address.append(row['ip_add'].strip())
    
    if not ip_address:
        print("No devices in list.")
        sys.exit(1)

    for ip in ip_address:
        device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': username,
        'password': password,
        }
        try:
            with ConnectHandler(**device) as conn:
                
                conn.enable()
                
                print(f"Connecting to {ip} ...")

                hostname = conn.find_prompt().strip('#>')

                print(f"Connection successful: {hostname} ({ip})")
                
                print(f"Backing up {ip} ...")

                backup_filename = f"{hostname}_{ip}.cfg"
                backup_filepath = os.path.join(backup_dir, backup_filename)
                
                config = conn.send_command('show running-config brief | exclude username | password | secret | aaa | trustpoint | certificate')

                with open(backup_filepath, 'w') as file_backup:
                    file_backup.write(config)
                
                print(f"Backup successful: {hostname} ({ip})")

                print(f"Collecting infos from {ip} ...")

                info_filename = f"{hostname}_{ip}.txt"
                info_filepath = os.path.join(info_dir, info_filename)

                ios_version = conn.send_command('show version | include Software,')
                inventory = conn.send_command('show inventory | section SN')
                cdp_neighbors = conn.send_command('show cdp neighbors')
                lldp_neighbors = conn.send_command('show lldp neighbors')
                l3interfaces = conn.send_command('show ip interface brief | exclude unassigned')
                routes = conn.send_command('show ip route vrf *')
                default_gateway = conn.send_command('show running-config | include default-gateway')
                vlans = conn.send_command('show vlan brief | include active')
                interface_status = conn.send_command('show interface status')

                with open(info_filepath, 'w') as file_info:
                    file_info.write(f"Hostname: {hostname}\n")
                    file_info.write(f"\nMGMT-IP: {ip}\n")
                    file_info.write(f"\nIOS-Version: {ios_version}\n")
                    file_info.write("\nInventory:\n")
                    for pid in inventory:
                        if len(pid.split()) >= 4:
                            file_info.write(f"{pid}\n")
                    file_info.write(f"\nCDP-Neighbors:\n {cdp_neighbors}\n")
                    file_info.write(f"\nLLDP-Neighbors:\n {lldp_neighbors}\n")
                    file_info.write("\nLayer 3 Interfaces:\n")
                    file_info.write(f"{l3interfaces}\n")
                    if "Gateway of last resort" in routes or "connected" in routes.lower():
                        file_info.write("\nRouting Table:\n")
                        file_info.write(f"{routes}\n")
                    else:
                        file_info.write("\nDefault Gateway:\n")
                        file_info.write(f"{default_gateway.strip()}\n")
                    file_info.write("\nVlans:\n")
                    file_info.write(f"{vlans}\n")
                    file_info.write("\nInterface Status:\n")
                    file_info.write(f"{interface_status}\n")
                    
                    print(f"Collection successful: {hostname} ({ip})")
        
        except exceptions.NetmikoAuthenticationException:
        
            af_filename = f"Auth_fail.txt"
            af_filepath = os.path.join(error_dir, af_filename)
        
            with open(af_filepath, 'a') as file_af:
                file_af.write(f"Authentication failed for {ip}\n")
                
                print(f"Authentication failed for {ip}")

        except exceptions.NetmikoTimeoutException:
            
            to_filename = f"Timeout.txt"
            to_filepath = os.path.join(error_dir, to_filename)
        
            with open(to_filepath, 'a') as file_to:
                file_to.write(f"Connection timeout to {ip}\n")

                print(f"Connection timeout to {ip}")
            
if __name__ == '__main__':
    main()