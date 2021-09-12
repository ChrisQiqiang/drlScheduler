class Scheduler(object):
    def __init__(self, env, algorithm):
        self.env = env
        self.algorithm = algorithm
        self.simulation = None
        self.cluster = None

    def attach(self, simulation):
        self.simulation = simulation
        self.cluster = simulation.cluster

    def make_decision(self):
        while True:
            machine, instance = self.algorithm(self.cluster, self.env.now)
            if machine is None or instance is None:
                break
            else:
                # pass # TODO reschedule instance
                self.cluster.instances_to_reschedule.pop(instance)
                machine.push(instance)

    def find_candidates(self):
        instances_to_reschedule = [inst for machine in self.cluster.machines_to_schedule for inst in
                                   machine.instances.values()]

        for inst in instances_to_reschedule:
            if inst.machine.to_schedule:
                inst.machine.to_schedule = False
                self.cluster.machines_to_schedule.remove(inst.machine)
            inst.machine.pop(inst.id)
        print("Instances to reschedule:", instances_to_reschedule)
        self.cluster.instances_to_reschedule = instances_to_reschedule

    def run(self):
        self.find_candidates()
        self.make_decision()
        yield self.env.timeout(1)
