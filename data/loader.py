import numpy as np
import pandas as pd
import os

from framework.instance import InstanceConfig
from framework.machine import MachineConfig


# def MachineConfigLoader(filename):  # id, cpu_capacity, memory_capacity, disk_capacity...
#     machine_configs = []
#     with open(filename) as f:
#         csv_reader = csv.reader(f)
#         for row in csv_reader:
#             machine_id, cpu_capacity, memory_capacity, disk_capacity = row[0], float(row[1]), float(row[2]), float(row[3])
#             machine_configs.append(MachineConfig(machine_id, cpu_capacity, memory_capacity, disk_capacity))
#     return machine_configs


# def InstanceConfigLoader(filename):
#     instance_configs = []
#     with open(filename) as f:
#         csv_reader = csv.reader(f)
#         for row in csv_reader:
#             inst_id, machine_id, cpu_curve, memory_curve, disk = row[0], row[2], [float(cpu) for cpu in row[3].split('|')], [float(memory) for memory in row[4].split('|')], float(row[5])
#             instance_configs.append(InstanceConfig(inst_id, machine_id, cpu_curve[0], memory_curve[0], disk, cpu_curve, memory_curve))
#     return instance_configs


def InstanceConfigLoader( vm_machine_id_file, vm_cpu_utils_folder):
    instance_configs = []
    # vm_cpu_requests = pd.read_csv(vm_cpu_request_file, header = None).values.squeeze()
    InstanceMachineId = pd.read_csv(vm_machine_id_file, header = None)[1].values
    vm_cpu_utils = sorted([os.path.join(vm_cpu_utils_folder, x) for x in os.listdir(vm_cpu_utils_folder)])


    for i in range(len(InstanceMachineId)):
        cpu_curve = pd.read_csv(vm_cpu_utils[i], header = None).values.squeeze().tolist()
        instance = InstanceConfig(i, InstanceMachineId[i], cpu_curve[0], cpu_curve)
        instance_configs.append(instance)
        
    return instance_configs