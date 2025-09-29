import paramiko
import time

# --- Device Connection Details (CHANGE THESE) ---
ROUTER_IP = "192.168.0.110"
ROUTER_USER = "admin"
ROUTER_PASS = "cisco"
ENABLE_PASS = "" # Password for the 'enable' command

# --- Configuration Details (CHANGE THESE) ---
INTERFACE_NAME = "GigabitEthernet0/2"
NEW_IP_ADDRESS = "192.168.5.1"
SUBNET_MASK = "255.255.255.0"

# --- SSH Client Setup ---
ssh_client = paramiko.SSHClient()
# Automatically add the server's host key (less secure, fine for labs)
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {ROUTER_IP}...")
    ssh_client.connect(hostname=ROUTER_IP,
                       username=ROUTER_USER,
                       password=ROUTER_PASS,
                       look_for_keys=False,
                       allow_agent=False)

    print("Connection successful. Getting interactive shell...")
    # Use invoke_shell() for interactive sessions like configuring a router
    shell = ssh_client.invoke_shell()
    shell.send('terminal length 0\n')  # Disable paging
    # Give the shell time to start
    time.sleep(2)

    # --- List of commands to execute ---
    commands = [
        f"enable\n",
        f"show ip interface brief\n",
        f"show version\n",
        f"show ip route\n",
    ]
    commands1 = [
        f"enable\n",
        f"{ENABLE_PASS}\n",
        f"configure terminal\n",
        f"interface {INTERFACE_NAME}\n",
        f"ip address {NEW_IP_ADDRESS} {SUBNET_MASK}\n",
        f"no shutdown\n", # Ensures the interface is administratively up
        f"end\n",
        f"write memory\n" # Saves the running-config to startup-config
    ]

    # --- Execute Commands ---
    print("Sending configuration commands...")
    for command in commands:
        shell.send(command)
        # Add a delay between commands to allow the device to process them
        time.sleep(1.5)

    # --- Capture and Print Output ---
    # The buffer might not capture everything if there's a lot of output,
    # but it's usually enough for configuration confirmation.
    output = shell.recv(65535).decode('utf-8')
    print("\n--- Router Output ---")
    print(output)
    print("--- End of Output ---\n")
    print("Configuration applied and saved successfully. ✅")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # --- Close the connection ---
    if ssh_client.get_transport() and ssh_client.get_transport().is_active():
        print("Closing SSH connection.")
        ssh_client.close()