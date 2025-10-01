import textfsm
import json
from datetime import datetime

# Paste the raw CLI output from your router here
raw_cli_output = """
R1#show ip interface brief
Interface             IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.0.110   YES DHCP   up                    up      
GigabitEthernet0/1    unassigned      YES NVRAM  administratively down down    
GigabitEthernet0/2    192.168.5.1     YES manual down                  down    
GigabitEthernet0/3    unassigned      YES NVRAM  administratively down down    
R1#show version
Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.7(3)M3, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2018 by Cisco Systems, Inc.
Compiled Wed 01-Aug-18 16:45 by prod_rel_team


ROM: Bootstrap program is IOSv

R1 uptime is 5 hours, 47 minutes
System returned to ROM by reload
System image file is "flash0:/vios-adventerprisek9-m"
Last reload reason: Unknown reason



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

Cisco IOSv (revision 1.0) with  with 460009K/62464K bytes of memory.
Processor board ID 9PJFAMWOL95KU50F23UK8
4 Gigabit Ethernet interfaces
DRAM configuration is 72 bits wide with parity disabled.
256K bytes of non-volatile configuration memory.
2097152K bytes of ATA System CompactFlash 0 (Read/Write)
0K bytes of ATA CompactFlash 1 (Read/Write)
1024K bytes of ATA CompactFlash 2 (Read/Write)
0K bytes of ATA CompactFlash 3 (Read/Write)



Configuration register is 0x0

R1#show ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is 192.168.0.1 to network 0.0.0.0

S* 0.0.0.0/0 [254/0] via 192.168.0.1
      192.168.0.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.0.0/24 is directly connected, GigabitEthernet0/0
L        192.168.0.110/32 is directly connected, GigabitEthernet0/0
R1#
"""


def parse_with_template(template_path, output):
    """Parses raw text with a given TextFSM template."""
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_data = fsm.ParseText(output)

        # Convert the list of lists to a list of dictionaries
        return [dict(zip(fsm.header, row)) for row in parsed_data]


def main():
    """Main function to orchestrate the parsing."""
    # Split the raw output by the command prompt to isolate each command's output
    # This is a simple way to do it; more robust methods exist
    command_outputs = raw_cli_output.split("R1#")

    show_ip_int_brief_output = [
        s for s in command_outputs if "show ip interface brief" in s
    ][0]
    show_version_output = [s for s in command_outputs if "show version" in s][0]
    show_ip_route_output = [s for s in command_outputs if "show ip route" in s][0]

    # Parse each section with its corresponding template
    interfaces = parse_with_template(
        "templates/cisco_ios_show_ip_interface_brief.textfsm", show_ip_int_brief_output
    )
    version_info = parse_with_template(
        "templates/cisco_ios_show_version.textfsm", show_version_output
    )
    routes = parse_with_template(
        "templates/cisco_ios_show_ip_route.textfsm", show_ip_route_output
    )

    # Combine everything into a single document for MongoDB
    device_data = {
        "hostname": "R1",  # You can parse this or set it manually
        "last_updated": datetime.utcnow().isoformat(),
        "version_info": version_info[0] if version_info else {},
        "interfaces": interfaces,
        "ip_routes": routes,
    }

    # Print the final JSON document, ready for MongoDB
    print(json.dumps(device_data, indent=2))

    # In a real script, you would insert this into MongoDB like so:
    # from pymongo import MongoClient
    # client = MongoClient('mongodb://localhost:27017/')
    # db = client['network_devices']
    # collection = db['device_states']
    # collection.insert_one(device_data)
    # print("Data inserted into MongoDB successfully.")


if __name__ == "__main__":
    main()
