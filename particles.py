import numpy as np
import uuid

simulation_speed = 0.001 # smaller -> more precise (+ latency)
interaction_cooldown_parameter = 0.005 # parameter for how long a particle has to wait until it can interact again. debuggung purposes only

class Particle:
    def __init__(self, type: str, speed, position, mass: float, radius: float): # Mass: kg
        self.id = str(uuid.uuid4())

        self.type = type  # 'neutron', 'uranium_235' etc.
        self.mass = mass
        self.radius = radius
        self.position = np.array(position, dtype=np.float64) # int -> float
        self.speed = np.array(speed, dtype=np.float64)

        self.cooldown = 0

    def distance(self, other_particle):
        if self.id == other_particle.id:  # Check based on unique random ID
            return -1.0
        distance = np.linalg.norm(self.position - other_particle.position)
        return distance

    def collision_interact(self, other_particle):
        if self.id == other_particle.id: # to avoid interaction with itself (redundant with code in simulation)
            return self

        self.cooldown = interaction_cooldown_parameter # to avoid endless interactions

        # attributes of particles
        m1 = self.mass
        m2 = other_particle.mass
        v1 = self.speed
        v2 = other_particle.speed

        # Apply the collision formula
        v1_new = (m1 - m2) / (m1 + m2) * v1 + (2 * m2) / (m1 + m2) * v2
        v2_new = (2 * m1) / (m1 + m2) * v1 + (m2 - m1) / (m1 + m2) * v2

        # Update speeds and cooldown
        self.speed = v1_new
        other_particle.update(v2_new)

        return self


    def update(self, speed): # updating attributes if other particle bumps into me
        self.speed = speed
        self.cooldown = interaction_cooldown_parameter


    def forward(self):
        """one timestep"""
        # one step in space
        self.position += self.speed * simulation_speed

        if self.cooldown > 0:
            self.cooldown -= simulation_speed
            if self.cooldown < 0:
                self.cooldown = 0  # ensure cooldown doesn't go below 0

