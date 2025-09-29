# File: parser_handler.py
# Description: A module for parsing command output using TextFSM.

from textfsm import clitable
import os


def parse_output_with_textfsm(command_output, template_file_name):
    """
    Parses the command output using a TextFSM template.
    Returns a list of dictionaries.

    Arguments:
        command_output (str): The raw output from the network device.
        template_file_name (str): The name of the TextFSM template file.

    Note: Assumes the 'ntc-templates' are installed and accessible.
    """
    # ❌ เพิ่มการตรวจสอบค่า None หรือค่าว่างเปล่าที่นี่
    if not command_output:
        print("❌ ข้อมูลนำเข้าสำหรับ TextFSM เป็นค่าว่าง. ไม่สามารถ parse ได้.")
        return []

    try:
        template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )
        index_file = "index"
        cli_table = clitable.CliTable(index_file, template_dir)

        # Select attributes and template based on command
        if "show_version" in template_file_name:
            attributes = {"Command": "show version", "Platform": "cisco_ios"}
        elif "show_ip_route" in template_file_name:
            attributes = {"Command": "show ip route", "Platform": "cisco_ios"}
        else:
            attributes = {"Command": "show ip interface brief", "Platform": "cisco_ios"}

        cli_table.ParseCmd(command_output, attributes)
        parsed_data = [dict(zip(cli_table.header, row)) for row in cli_table]
        return parsed_data

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการ parse ด้วย TextFSM: {e}")
        return []
