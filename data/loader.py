import numpy as np
import pandas as pd
import os

from framework.instance import InstanceConfig
from framework.machine import MachineConfig


def InstanceConfigLoader(vm_machine_id_file, vm_cpu_utils_folder):
    instance_configs = []
    # vm_cpu_requests = pd.read_csv(vm_cpu_request_file, header = None).values.squeeze()
    vm_machine_ids = pd.read_csv(vm_machine_id_file, header = None)[0].values
    vm_cpu_utils = sorted([os.path.join(vm_cpu_utils_folder, x) for x in os.listdir(vm_cpu_utils_folder)])
    # for all trace
    for i in range(len(vm_cpu_utils)):
        cpu_curve = pd.read_csv(vm_cpu_utils[i], header = None).values.squeeze().tolist()
        instance = InstanceConfig(i, cpu_curve[0], cpu_curve)
        instance_configs.append(instance)
    return instance_configs

def MachineConfigLoader(InputFile):
    vm_machines_cpu_num = pd.read_csv(InputFile, header=None)[1].values
    return [MachineConfig(i, cpu_num) for i, cpu_num in enumerate(vm_machines_cpu_num)]