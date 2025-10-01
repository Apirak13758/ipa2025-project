# ==============================================================================

# File: ssh_handler.py
# Description: A module for handling SSH connections and command execution.

import paramiko
import time


def ssh_connect_and_run(ip, username, password, command_type, details={}):
    print(details)
    output = ""
    ssh_client = paramiko.SSHClient()

    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # --- เพิ่มบรรทัดนี้เพื่อแก้ไขปัญหา key exchange ---
        # paramiko.transport.Transport._preferred_ciphers = (
        #     'aes128-cbc', '3des-cbc', 'aes192-cbc', 'aes256-cbc'
        # )
        paramiko.transport.Transport._preferred_kex = (
            "diffie-hellman-group-exchange-sha1",
            "diffie-hellman-group14-sha1",
            "diffie-hellman-group1-sha1",
        )

        print(f"🔗 กำลังเชื่อมต่อ SSH ไปยัง {ip}...")
        ssh_client.connect(
            hostname=ip,
            username=username,
            password=password,
            allow_agent=False,
            look_for_keys=False,
            disabled_algorithms=dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"]),
        )

        print("Connection successful. Getting interactive shell...")
        # Use invoke_shell() for interactive sessions like configuring a router
        shell = ssh_client.invoke_shell()
        shell.send("terminal length 0\n")  # Disable paging
        # Give the shell time to start
        time.sleep(2)

        # --- List of commands to execute ---
        commands = [
            "enable\n",
            "show ip interface brief\n",
            "show version\n",
            "show ip route\n",
        ]

        commands1 = [
            "enable\n",
            f"{details.get('ENABLE_PASS', '')}\n",
            "configure terminal\n",
            f"interface {details.get('INTERFACE_NAME', '')}\n",
            f"ip address {details.get('NEW_IP_ADDRESS', '')} {details.get('SUBNET_MASK', '')}\n",
            "no shutdown\n",  # Ensures the interface is administratively up
            "end\n",
            "write memory\n",  # Saves the running-config to startup-config
        ]

        if command_type == "show":
            final_command = commands
        elif command_type == "config":
            final_command = commands1 + commands
        else:
            print("Invalid command type.")
            return ""

        # --- Execute Commands ---
        print("Sending configuration commands...")
        for command in final_command:
            shell.send(command)
            # Add a delay between commands to allow the device to process them
            time.sleep(1.5)

        # --- Capture and Print Output ---
        # The buffer might not capture everything if there's a lot of output,
        # but it's usually enough for configuration confirmation.
        output = shell.recv(65535).decode("utf-8")
        print("\n--- Router Output ---")
        print(output)
        print("--- End of Output ---\n")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ SSH: {e}")
    finally:
        if ssh_client:
            ssh_client.close()
            print("SSH connection closed.")
    return output
