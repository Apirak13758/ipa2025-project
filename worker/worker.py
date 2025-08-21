# File: main_worker.py
# Description: This is the main entry point for the RabbitMQ worker.
# It handles message consumption and calls functions from other modules to perform tasks.

import pika
import json
from ssh_handler import ssh_connect_and_run
from db_handler import save_to_mongo
from parser_handler import parse_output_with_textfsm
import os, time

# --- การตั้งค่า (Configuration) ---
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_QUEUE = 'router_jobs'
TEXTFSM_TEMPLATE = 'cisco_ios_show_ip_interface_brief.textfsm'

# --- ฟังก์ชัน Callback สำหรับ RabbitMQ ---

def on_message_callback(ch, method, properties, body):
    """
    This function is called whenever a message is received from the RabbitMQ queue.
    It orchestrates the entire automation process.
    """
    print(f"📥 ได้รับข้อความ: {body.decode()}")
    
    try:
        # 1. Decode and parse the JSON message body
        message_data = json.loads(body.decode())
        
        ip = message_data.get('ip')
        username = message_data.get('username')
        password = message_data.get('password')
        command = "show ip interface brief"  # The command to execute
        
        if not all([ip, username, password]):
            print("❌ ข้อมูลไม่ครบถ้วนในข้อความ. ต้องมี 'ip', 'username', 'password'.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 2. SSH to the device and get command output
        command_output = ssh_connect_and_run(ip, username, password, command)
        
        if not command_output:
            print("❌ ไม่ได้รับข้อมูลจากอุปกรณ์. ยกเลิกการประมวลผล.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"Received job for router {ip}")
        print(command_output)

        # 3. Parse the output using TextFSM
        parsed_data = parse_output_with_textfsm(command_output, TEXTFSM_TEMPLATE)
        
        if not parsed_data:
            print("❌ ไม่สามารถ parse ข้อมูลได้. โปรดตรวจสอบ template และรูปแบบข้อมูล.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(json.dumps(parsed_data, indent=2))
        
        # 4. Save the parsed data to MongoDB
        save_to_mongo(parsed_data, ip)
        print(f"Stored interface status for {ip}")
        
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
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)

        print(f" [*] กำลังรอข้อความในคิว '{RABBITMQ_QUEUE}'. กด CTRL+C เพื่อออก.")
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=on_message_callback)
        channel.start_consuming()
        
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ ไม่สามารถเชื่อมต่อกับ RabbitMQ ได้: {e}")
        print("โปรดตรวจสอบว่า RabbitMQ Server กำลังทำงานอยู่หรือไม่ หรือการตั้งค่าถูกต้อง.")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        
if __name__ == "__main__":
    INTERVAL = 60.0
    next_run = time.monotonic()
    count = 0

    while True:
        now = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        ms = int((now % 1) * 1000)  
        now_str_with_ms = f"{now_str}.{ms:03d}"
        print(f"[{now_str_with_ms}] run #{count}")
        start_listening()
        count += 1
        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))