simulation_speed = 0.001 # smaller -> more precise
interaction_cooldown = 10 # parameter for how long a particle has to wait until it can interact again. debuggung purposes only

class Particle:
    def __init__(self, type: str, speed: list[float] = [0,0,0], mass: float, position: list[float] = [0, 0, 0]): # energy: Joule, Mass: kg
        self.type = type  # 'neutron' or 'uranium'
        self.mass = mass
        self.position = position

        self.speed = speed

        self.has_interaction = 0


    def interact(self, other_particle):
        self.has_interaction = interaction_cooldown

        self.speed = # calculation based on impact
        self.energy =
        pass

    def forward(self):
        # one timestep
        self.position += self.speed * simulation_speed

        if not self.has_interaction:
            self.has_interaction += -1 * simulation_speed
            return None

#       elif self.position very close to other position (HNSW + pythagoras):
#            self.interact(other_particle)
#               other_particle.interact(self)



        pass

