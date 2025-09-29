"""
File: main_worker.py
Description: This is the main entry point for the RabbitMQ worker.
It handles message consumption and calls functions
from other modules to perform tasks.
"""

import pika
import json
from ssh_handler import ssh_connect_and_run
from db_handler import save_to_mongo
from parser_handler import parse_output_with_textfsm
import os
import time

# --- การตั้งค่า (Configuration) ---
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_QUEUE = "router_jobs"
TEXTFSM_TEMPLATE = "cisco_ios_show_ip_interface_brief.textfsm"
user = os.getenv("RABBIT_USERNAME")
pwd = os.getenv("RABBIT_PASSWORD")


# --- ฟังก์ชัน Callback สำหรับ RabbitMQ ---
def on_message_callback(ch, method, properties, body):
    """
    This function is called whenever
    a message is received from the RabbitMQ queue.
    It orchestrates the entire automation process.
    """
    print(f"📥 ได้รับข้อความ: {body.decode()}")

    try:
        # 1. Decode and parse the JSON message body
        message_data = json.loads(body.decode())

        ip = message_data.get("ip")
        username = message_data.get("username")
        password = message_data.get("password")
        command_type = message_data.get("command_type")
        details = message_data.get("details", {})

        if not all([ip, username, password]):
            print("❌ ข้อมูลไม่ครบถ้วนในข้อความ.'ip', 'username', 'password'.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 2. SSH to the device and get combined output
        command_output = ssh_connect_and_run(ip, username, password, command_type, details)

        if not command_output:
            print("❌ ไม่ได้รับข้อมูลจากอุปกรณ์. ยกเลิกการประมวลผล.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"Received job for router {ip}")
        print(command_output)

        # 3. Split combined output into sections for each command
        # Assume each command output starts with a unique marker, e.g., '--- show ip route ---', etc.
        sections = {}
        current_cmd = None
        for line in command_output.splitlines():
            if "show ip interface brief" in line.lower():
                current_cmd = "show ip interface brief"
                sections[current_cmd] = []
            elif "show ip route" in line.lower():
                current_cmd = "show ip route"
                sections[current_cmd] = []
            elif "show version" in line.lower():
                current_cmd = "show version"
                sections[current_cmd] = []
            elif current_cmd:
                sections[current_cmd].append(line)
        print(sections)

        # 4. Parse each section with the correct TextFSM template
        parsed_results = {}
        for cmd, output_lines in sections.items():
            output = "\n".join(output_lines)
            if cmd == "show ip interface brief":
                template_file = "cisco_ios_show_ip_interface_brief.textfsm"
            elif cmd == "show ip route":
                template_file = "cisco_ios_show_ip_route.textfsm"
            elif cmd == "show version":
                template_file = "cisco_ios_show_version.textfsm"
            else:
                continue
            parsed = parse_output_with_textfsm(output, template_file)
            parsed_results[cmd] = parsed
        print(parsed_results)

        print(json.dumps(parsed_results, indent=2))

        # 5. Save all parsed results to MongoDB
        save_to_mongo(parsed_results, ip)
        print(f"Stored parsed results for {ip}")

    except json.JSONDecodeError:
        print("❌ เกิดข้อผิดพลาด: ไม่สามารถ parse JSON จากข้อความได้.")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
    finally:
        # 5. Acknowledge the message to RabbitMQ, indicating it's processed
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("--- การประมวลผลข้อความเสร็จสิ้น ---")


# --- วนลูปหลักเพื่อรอรับข้อความ ---
def start_listening():
    """
    Starts the RabbitMQ consumer to listen for messages in a queue.
    """
    try:
        creds = pika.PlainCredentials(user, pwd)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBITMQ_HOST, credentials=creds)
        )
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)

        print(f" [*] กำลังรอข้อความในคิว '{RABBITMQ_QUEUE}'.")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=RABBITMQ_QUEUE, on_message_callback=on_message_callback
        )
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ ไม่สามารถเชื่อมต่อกับ RabbitMQ ได้: {e}")
        print("โปรดตรวจสอบว่า RabbitMQ Server กำลังทำงานอยู่หรือไม่.")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
    INTERVAL = 5.0
    next_run = time.monotonic()

    while True:
        now = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        ms = int((now % 1) * 1000)
        now_str_with_ms = f"{now_str}.{ms:03d}"
        start_listening()
        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))
