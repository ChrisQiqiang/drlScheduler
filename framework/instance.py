class InstanceConfig(object):
    def __init__(self, instance_id, cpu , cpu_curve=None):
        self.id = instance_id
        self.machine_id = 0
        self.cpu = cpu
        self.cpu_curve = cpu_curve

class Instance(object):
    def __init__(self, instance_config):
        self.id = instance_config.id
        self.cpu = instance_config.cpu
#         self.memory = instance_config.memory
#         self.disk = instance_config.disk
        self.machine = None

    def attach(self, machine):
        self.machine = machine

