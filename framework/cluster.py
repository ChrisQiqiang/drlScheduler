from framework.machine import Machine
import warnings

class Cluster(object):
    def __init__(self):
        self.machines = {}
        self.machines_to_schedule = set()
        self.instances_to_reschedule = None

    def configure_machines(self, machine_configs):
        for machine_config in machine_configs:
            machine = Machine(machine_config)
            self.machines[machine.id] = machine
            machine.attach(self)

    def SearchFirstFitMachineForInstance(self, instance_config):
        for machine in self.machines.values():
            if machine.cpu > instance_config.cpu:
                return machine
        return None

    def configure_instances(self, instance_configs):
        for instance_config in instance_configs:
            machine = self.SearchFirstFitMachineForInstance(instance_config)
            if machine is None:
                warnings.warn("None of machines in the cluster can launch INSTANCE" + instance_config.instance_id + " , please recommit it later...")
            else:
                machine.add_instance(instance_config)


#     @property
#     def structure(self):
#         return {
#             i: {
#                     'cpu_capacity': m.cpu_capacity,
#                     'memory_capacity': m.memory_capacity,
#                     'disk_capacity': m.disk_capacity,
#                     'cpu': m.cpu,
#                     'memory': m.memory,
#                     'disk': m.disk,
#                     'instances': {
#                         j: {
#                             'cpu': inst.cpu,
#                             'memory': inst.memory,
#                             'disk': inst.disk
#                         } for j, inst in m.instances.items()
#                     }
#                 }
#             for i, m in self.machines.items()
#         }

    @property
    def structure(self):
        return {
            i: {
                    'cpu_capacity': m.cpu_capacity,
                    'cpu': m.cpu,
                    'instances': {
                        j: {
                            'cpu': inst.cpu,
                        } for j, inst in m.instances.items()
                    }
                }
            for i, m in self.machines.items()
        }