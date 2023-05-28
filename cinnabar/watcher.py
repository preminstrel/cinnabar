from paramiko.config import SSHConfig
from fabric import Connection
from termcolor import cprint, colored
import datetime
from sqlalchemy.dialects.postgresql import insert
import os

def get_hostnames_and_ips_from_ssh_config():
    ssh_config_path = os.path.expanduser('~/.ssh/config')
    config = SSHConfig()

    with open(ssh_config_path, 'r') as config_file:
        config.parse(config_file)

    hostnames_and_ips = {}
    for host in config.get_hostnames():
        if host != '*':
            hostname = host
            ip = config.lookup(host)['hostname']
            hostnames_and_ips[hostname] = ip

    return hostnames_and_ips

def old_process_nvidia_smi_output(smi_output: str) -> dict:
    r"""Sat May 20 04:31:21 2023
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 510.108.03   Driver Version: 510.108.03   CUDA Version: 11.6     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |                               |                      |               MIG M. |
    |===============================+======================+======================|
    |   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0 Off |                  N/A |
    |  0%   83C    P2   171W / 420W |  11015MiB / 24576MiB |     18%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+
    |   1  NVIDIA GeForce ...  Off  | 00000000:08:00.0 Off |                  N/A |
    | 57%   61C    P2   321W / 420W |   9459MiB / 24576MiB |    100%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+
                                                                                
    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
    |        ID   ID                                                   Usage      |
    |=============================================================================|
    |    0   N/A  N/A      1429      G   /usr/lib/xorg/Xorg                  9MiB |
    |    0   N/A  N/A      1568      G   /usr/bin/gnome-shell                8MiB |
    |    0   N/A  N/A    563099      C   python                          10981MiB |
    |    1   N/A  N/A      1429      G   /usr/lib/xorg/Xorg                  4MiB |
    |    1   N/A  N/A   1149688      C   python                           9451MiB |
    +-----------------------------------------------------------------------------+
    """
    # Split on newlines
    lines = smi_output.split("\n")
    # Remove any lines that don't contain '|', which are just blank lines
    lines = [line for line in lines if "|" in line]
    
    # remain the lines contain MB   
    lines = [line for line in lines if "MiB" in line and "%" in line]
    
    # clean the lines and only remain memory usage
    lines_memory = [line.split("|")[2] for line in lines] 
    # convert MiB to GB
    lines_memory_used = [line.split("/")[0].strip() for line in lines_memory]
    lines_memory_used = [line.split("MiB")[0].strip() for line in lines_memory_used]
    lines_memory_used = [f"{int(line)/1024:.0f}GB" for line in lines_memory_used]
    
    lines_memory_total = [line.split("/")[1].strip() for line in lines_memory]
    lines_memory_total = [line.split("MiB")[0].strip() for line in lines_memory_total]
    lines_memory_total = [f"{int(line)/1024:.0f}GB" for line in lines_memory_total]

    line_util = [line.split("|")[3] for line in lines]
    # remove default
    line_util = [line.split("Default")[0] for line in line_util]

    # print them
    gpu = {}
    for i in range(len(lines_memory)):
        # add gpu id
        gpu[f"GPU {i}"] = {}
        gpu[f"GPU {i}"]["memory_used"] = lines_memory_used[i]
        gpu[f"GPU {i}"]["memory_total"] = lines_memory_total[i]
        gpu[f"GPU {i}"]["util"] = line_util[i].replace(" ","")

    return gpu

def process_nvidia_smi_output(smi_output: str) -> dict:
    r"""
    0, NVIDIA GeForce RTX 3090, 97, 24576, 15276, 91
    1, NVIDIA GeForce RTX 3090, 100, 24576, 23907, 64
    """
    lines = smi_output.split("\n")
    gpu = {}
    for line in lines:
        index, name, utilization, memory_total, memory_used, temperature = line.split(',')
        gpu[f"GPU {index}"] = {}
        gpu[f"GPU {index}"]["name"] = name
        gpu[f"GPU {index}"]["utilization"] = utilization
        gpu[f"GPU {index}"]["memory_total"] = round(int(memory_total)/1024)
        gpu[f"GPU {index}"]["memory_used"] = round(int(memory_used)/1024)
        gpu[f"GPU {index}"]["temperature"] = temperature
    return gpu

def get_gpu_status(connection):
    result = connection.run("nvidia-smi --query-gpu=index,name,utilization.gpu,memory.total,memory.used,temperature.gpu --format=csv,noheader,nounits", hide=True)

    if result.return_code != 0:
        return {
            "code": -1,
            "message": f"Error with server {result.host}: {result.stderr.strip()}"
        }
    else:
        return process_nvidia_smi_output(result.stdout.strip())
    
def get_cpu_status(connection):
    result = connection.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'", hide=True)

    if result.return_code != 0:
        print(f"Error with server {result.host}: {result.stderr}")
        return None
    else:
        return f"{result.stdout.strip()}%"

def get_memory_status(connection):
    result = connection.run("free | grep 'Mem:'", hide=True)

    # Convert the byte string to a regular string
    output_str = result.stdout.strip()

    # Split the string into a list of values
    values = output_str.split()

    # Extract the used memory and total memory values
    used_memory = int(values[2])
    total_memory = int(values[1])
    
    # convert byte to GB
    used_memory = round(used_memory / 1024 / 1024, 2)
    total_memory = round(total_memory / 1024 / 1024, 2)

    if result.return_code != 0:
        print(f"Error with server {result.host}: {result.stderr}")
        return None
    else:
        return {
            "used_memory": used_memory,
            "total_memory": total_memory,
        }

def get_os(connection):
    result = connection.run("cat /etc/os-release", hide=True)

    if result.return_code != 0:
        print(f"Error with server {result.host}: {result.stderr}")
        return None
    else:
        os_info = result.stdout.strip()
        os_lines = os_info.split('\n')
        os_dict = {}

        for line in os_lines:
            key, value = line.split('=', 1)
            os_dict[key] = value.strip('"')

        pretty_name = os_dict.get('PRETTY_NAME')
        if pretty_name:
            return pretty_name

        name = os_dict.get('NAME')
        version = os_dict.get('VERSION')
        if name and version:
            return f"{name} {version}"

def get_ip(connection):
    result = connection.run("curl -s ifconfig.me", hide=True)

    if result.return_code != 0:
        print(f"Error with server {result.host}: {result.stderr}")
        return None
    else:
        return result.stdout.strip()

def get_hostname(connection):
    result = connection.run("hostname", hide=True)

    if result.return_code != 0:
        print(f"Error with server {result.host}: {result.stderr}")
        return None
    else:
        return result.stdout.strip()

def get_conda_envs(connection):
    user = connection.user
    result = connection.run(command=f'/home/{user}/anaconda3/bin/conda info --env', hide=True, warn=True)
    env_list = []
    if result.ok:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split(' ')
            if len(parts) >= 2:
                env_list.append(parts[0].strip())
    if '#' in env_list:
        env_list.remove('#')
    return env_list

def get_free_gpu(connection):
    gpu_status = get_gpu_status(connection)
    # {"GPU 0": {"name": " NVIDIA GeForce RTX 3090", "utilization": " 77", "memory_total": 24, "memory_used": 15, "temperature": " 89"}, "GPU 1": {"name": " NVIDIA GeForce RTX 3090", "utilization": " 95", "memory_total": 24, "memory_used": 23, "temperature": " 57"}}
    free_gpu = []
    for key, value in gpu_status.items():
        if int(value["memory_used"]) < 11:
            free_gpu.append(key.split(" ")[-1])
    return free_gpu
