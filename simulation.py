import particles
from particles import Particle, simulation_speed
import numpy as np
import plotly.graph_objects as go
import time
import random


# Parameters
sigma_0 = 580  # Fission cross-section for thermal neutrons in barns
sigma_thermal = 580  # Maximum fission cross-section for thermal neutrons in barns
E_0 = 0.025  # Reference energy in eV (typical for thermal neutrons)
alpha = 0.8  # Empirical constant (typically between 0.5 and 1)

# Function to calculate the fission probability




class Simulation:

    def __init__(self, simulation_steps, neutrons_start: int = 10, uranium_start: int = 10):
        self.simulation_steps = simulation_steps
        self.neutrons_start = neutrons_start
        self.uranium_start = uranium_start

        # constants
        self.mass_neutron = 1.675 * 10 ** -27
        self.radius_neutron = 8 * 10 ** -16
        self.mass_uranium_235 = 3.91 * 10 ** -25
        self.radius_uranium = 1.5 * 10

    def _innitialize_particles(self):
        """creating initial particles"""

        particles = []
        def random_unit_vector():
            vec = np.random.normal(0.0, 1.0, 3)
            norm = np.linalg.norm(vec)
            if norm == 0:
                return np.array([1.0, 0.0, 0.0])
            return vec / norm

        # instance particle objects of type neutron
        for i in range(self.neutrons_start):
            speed_mag = np.random.uniform(2000, 2200)
            speed_vector = random_unit_vector() * speed_mag
            position_vector = np.random.uniform(0, 100, 3)
            particles.append(Particle("neutron", speed_vector, position_vector, self.mass_neutron, self.radius_neutron))
        print(f"created {self.neutrons_start} neutron particles")

        # instance particle objects of type uranium
        for i in range(self.uranium_start):
            speed_mag = np.random.uniform(0, 10)
            speed_vector = random_unit_vector() * speed_mag
            position_vector = np.random.uniform(0, 100, 3)
            particles.append(Particle("uranium_235", speed_vector, position_vector, self.mass_uranium_235, self.radius_uranium))
        print(f"created {self.uranium_start} Uranium particles")

        return particles




    def _fission_probability(self, v1, v2):
        if v1.all() == v2.all():
            return 0,0
        v_dif = np.linalg.norm(v1 - v2)  # speed difference
        probability = (sigma_0 / sigma_thermal) * (5.22e-2 * v_dif ** 2 / E_0) ** (-alpha)
        return probability, v_dif



    def _check_for_collision(self, particle, possible_neighbour):
        if particle.cooldown == 0 and possible_neighbour.cooldown == 0:  # both havent just interacted, to avoid endless interactions

            distance = particle.distance(possible_neighbour)

            collision_distance = particle.radius + possible_neighbour.radius

            if distance <= collision_distance and distance != -1.0:  # if two particles are very close but NOT the same particle -> interaction
                return True

            else: return False

        else: return False



    def _execute_collision_or_interaction(self, particle, possible_neighbour):
        if (particle.type == "uranium_235" and possible_neighbour.type == "neutron") or (
                particle.type == "neutron" and possible_neighbour.type == "uranium_235"):
            fission_prob, v_dif = self._fission_probability(particle.speed, possible_neighbour.speed)
            fission_prob = 0.1

            if random.random() < fission_prob:
                speed_new_neutron = np.cross(particle.speed, possible_neighbour.speed) # cross product for new speed vector, won't interfere with either of other particle and speed dimension is right
                position_new_neutron = particle.position + speed_new_neutron * simulation_speed # to not interact directly again.
                new_neutron = Particle(type ="neutron",position = position_new_neutron, speed = speed_new_neutron, mass = self.mass_neutron, radius= self.radius_neutron)
                return new_neutron

            else:
                # normal interaction
                v = np.linalg.norm(particle.speed - possible_neighbour.speed)
                particle.collision_interact(possible_neighbour)
                return None
        else:
            # normal interaction
            particle.collision_interact(possible_neighbour)
            return None

    def one_simulation_step(self, particles):
        new_particles = []
        for particle in particles:
            if np.any(np.abs(particle.position) > 100):
                particle.speed = particle.speed * -1




            particle.forward() # move in space

            for possible_neighbour in particles: # check for collisions with ALL other particles (very inefficient and bad scaling ik=)
                if self._check_for_collision(particle, possible_neighbour):
                    spawned = self._execute_collision_or_interaction(particle, possible_neighbour)
                    if spawned is not None:
                        new_particles.append(spawned)

        if new_particles:
            particles.extend(new_particles)

        return len(new_particles)


    def simulate(self):
        particles = self._innitialize_particles()
        for i in range(self.simulation_steps):
            self.one_simulation_step(particles)



if __name__ == "__main__":
    simulation = Simulation(3)
    simulation.simulate()
