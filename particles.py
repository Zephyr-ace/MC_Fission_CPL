import numpy as np

simulation_speed = 0.001 # smaller -> more precise
interaction_cooldown_parameter = 10 # parameter for how long a particle has to wait until it can interact again. debuggung purposes only

class Particle:
    def __init__(self, type: str, speed, position, mass: float): # Mass: kg
        self.type = type  # 'neutron', 'uranium_235' etc.
        self.mass = mass
        self.position = np.array(position, dtype=np.float64) # int -> float
        self.speed = np.array(speed, dtype=np.float64)

        self.cooldown = 0


    def interact(self, other_particle):
        self.cooldown = interaction_cooldown_parameter

        m1 = self.mass
        m2 = other_particle.mass
        v1 = self.speed
        v2 = other_particle.speed

        # calculation based on impact speeds an masses
        v1 = (m1-m2)/(m1+m2)*v1 + (2*m2)/(m1+m2)*v2
        v2 = (2*m1)/(m1+m2)*v1  + (m2-m1)/(m1+m2)*v2

        # updating attributes
        self.speed = v1
        other_particle.update(v2)


    def update(self, speed: list[float]): # updating attributes if other particle bumps into me
        self.speed = speed
        self.cooldown = interaction_cooldown_parameter


    def forward(self):
        """one timestep"""

        # cool down


        # one step in space
        self.position += self.speed * simulation_speed

        if self.cooldown > 0:
            self.cooldown += -1
            return None

