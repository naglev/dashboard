import os
import subprocess
from .text_processors import *


def license_status(software_name):
    
    license_servers = {
        'software1' : {
            'cmd_expression': 'lmutil lmstat -a -c 1000@192.168.1.1',
            'text_processor': software1_text_processor
        },
        'software2': {
            'cmd_expression': 'lmutil lmstat -a -c 1000@192.168.1.1',
            'text_processor': software2_text_processor
        },
        'software3': {
            'cmd_expression': 'lmxendutil -licstatxml -host 192.168.1.1 -port 1000',
            'text_processor': software3_text_processor
        },
        'software4': {
            'cmd_expression': 'MDLMUtil -licstatxml -host 192.168.1.1 -port 1000',
            'text_processor': software4_text_processor
        },
    }


    basedir = os.path.abspath(os.path.dirname(__file__))
    tools_folder = os.path.join(basedir, "tools")

    cmd_expression = f"{tools_folder}\{license_servers[software_name]['cmd_expression']}"
    server_response = subprocess.getoutput(cmd_expression)

    text_processor = license_servers[software_name]['text_processor']
    license_list = text_processor(server_response)

    return license_list


if __name__ == '__main__':
    print(license_status('software2'))
