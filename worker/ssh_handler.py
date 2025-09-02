# ==============================================================================

# File: ssh_handler.py
# Description: A module for handling SSH connections and command execution.

import paramiko


def ssh_connect_and_run(ip, username, password, command):
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

        print(f"▶️ กำลังรันคำสั่ง: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8").strip()

        error_output = stderr.read().decode("utf-8").strip()
        if error_output:
            print(f"⚠️ มีข้อผิดพลาดจาก SSH: {error_output}")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ SSH: {e}")
    finally:
        if ssh_client:
            ssh_client.close()
            print("SSH connection closed.")
    return output
