class Monitor(object):
    def __init__(self, env, trigger, algorithm):
        self.env = env
        self.trigger = trigger
        self.algorithm = algorithm
        self.simulation = None
        self.cluster = None

    def attach(self, simulation):
        self.simulation = simulation
        self.cluster = simulation.cluster

    def sample(self):
        for instance, instance_cpu_curve in self.simulation.instance_cpu_curves.items():
            instance.cpu = instance_cpu_curve.pop(0)
#         for instance, instance_memory_curve in self.simulation.instance_memory_curves.items():
#             instance.memory = instance_memory_curve.pop(0)
        return True

    def make_decision(self):
        while True:
            machine, instance = self.algorithm(self.cluster, self.env.now)
            if machine is None or instance is None:
                break
            else:
                # pass # TODO reschedule instance (Done)
                self.cluster.instances_to_reschedule.remove(instance)
                machine.push(instance)
                print("Instance", instance.id, "has been scheduled to Machine", machine.id)

    def find_candidates(self):
        instances_to_reschedule = [inst for machine in self.cluster.machines_to_schedule for inst in
                                   machine.instances.values()]

        for inst in instances_to_reschedule:
            if inst.machine.to_schedule:
                inst.machine.to_schedule = False
                self.cluster.machines_to_schedule.remove(inst.machine)
            inst.machine.pop(inst.id)
        print("Instances to reschedule:",[inst.id for inst in instances_to_reschedule])
        self.cluster.instances_to_reschedule = instances_to_reschedule

    def run(self):
        while not self.simulation.finished:
            self.sample()
            self.trigger(self.cluster, self.env.now)
            if self.cluster.machines_to_schedule:
                print('At', self.env.now, 'scheduler was triggered!')
                print("Machines are over utilized:", [machine.id for machine in self.cluster.machines_to_schedule])
                self.find_candidates() # 选择迁出vm
                self.make_decision() # 选择迁入host
                yield self.env.timeout(1)
            yield self.env.timeout(300)
        print("Env time:", self.env.now)
