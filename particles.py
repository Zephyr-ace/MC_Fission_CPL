class Particle:
    def __init__(self, type, energy):
        self.type = type  # 'neutron' or 'uranium'
        self.energy = energy  # Energy of the particle
        self.speed = 1

    def interact(self, other_particle):
        pass

    def forward(self):
        # one timestep
        pass

