import particles
from particles import Particle, simulation_speed
import numpy as np
import plotly.graph_objects as go
import time
import random
from parameters import sigma_0, sigma_thermal, E_0, alpha, bounding_parameter, neutron_speed_magnitude, \
    radius_multiplicator, neutron_init_speed, fission_prob_hardcoded_parameter, speed_magnitude_new_products

class Simulation:

    def __init__(self, simulation_steps, neutrons_start: int = 10, uranium_start: int = 10):
        self.simulation_steps = simulation_steps
        self.neutrons_start = neutrons_start
        self.uranium_start = uranium_start

        # constants
        self.mass_neutron = 1.675 * 10 ** -27
        self.radius_neutron = 8 * 10 ** -16
        self.mass_uranium_235 = 3.91 * 10 ** -25
        self.radius_uranium = 1.4 * 10**-10
        self.mass_barium = 2.28 * 10 ** -25
        self.radius_barium = 0.8 * 10**-10
        self.mass_krypton = 1.39 * 10 ** -25
        self.radius_krypton = 0.88 * 10**-10

    def _innitialize_particles(self):
        """creating initial particles"""

        particles = []

        # instance particle objects of type neutron
        for i in range(self.neutrons_start):
            speed_mag = np.random.uniform(neutron_init_speed, 1.5* neutron_init_speed)
            speed_vector = self.random_unit_vector() * speed_mag
            position_vector = np.random.uniform(low = -bounding_parameter*0.9, high= bounding_parameter*0.9, size=3)
            particles.append(Particle("neutron", speed_vector, position_vector, self.mass_neutron, self.radius_neutron))


        # instance particle objects of type uranium
        for i in range(self.uranium_start):
            speed_mag = np.random.uniform(0, 100)
            speed_vector = self.random_unit_vector() * speed_mag
            position_vector = np.random.uniform(-bounding_parameter*0.9, bounding_parameter*0.9, 3)
            particles.append(Particle("uranium_235", speed_vector, position_vector, self.mass_uranium_235, self.radius_uranium))


        return particles

    def random_unit_vector(self):
        vec = np.random.normal(0.0, 1.0, 3)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return np.array([1.0, 0.0, 0.0])
        return vec / norm


    def _fission_probability(self, v1, v2):
        if v1.all() == v2.all():
            return 0,0
        v_dif = np.linalg.norm(v1 - v2)  # speed difference
        probability = (sigma_0 / sigma_thermal) * (5.22e-2 * v_dif ** 2 / E_0) ** (-alpha)
        return probability, v_dif



    def _check_for_collision(self, particle, possible_neighbour):
        if particle.cooldown == -1 or possible_neighbour.cooldown == -1: # no interaction if one is marked as deleted
            return False

        elif particle.cooldown == 0 or particle.cooldown != possible_neighbour.cooldown:  # particles have not just interacted, to avoid endless interactions or add and possible_neighbour.cooldown == 0
            if particle.id == possible_neighbour.id: # redundant but secure
                return False

            displacement = particle.position - possible_neighbour.position
            distance_sq = np.dot(displacement, displacement)
            collision_distance = (particle.radius + possible_neighbour.radius) * radius_multiplicator

            if distance_sq <= collision_distance ** 2:  # if two particles are very close -> interaction
                return True

            else: return False

        else: return False



    def _execute_collision_or_interaction(self, particle, possible_neighbour):
        if (particle.type == "uranium_235" and possible_neighbour.type == "neutron") or (
                particle.type == "neutron" and possible_neighbour.type == "uranium_235"):
            fission_prob, v_dif = self._fission_probability(particle.speed, possible_neighbour.speed)
            if fission_prob_hardcoded_parameter is not None:
                fission_prob = fission_prob_hardcoded_parameter # for the simulation to work with fewer particles.

            if random.random() < fission_prob:

                # create 2-3 new neutrons <<<
                a = 2
                if random.random() < 0.5:
                    a = 3

                new_neutrons = []
                speed_new_neutron_direction = np.cross(particle.speed, possible_neighbour.speed)  # won't interfere with either of other particles
                speed_new_neutron_norm = speed_new_neutron_direction / np.linalg.norm(speed_new_neutron_direction)

                for i in range(a):
                    speed_new_neutron = neutron_speed_magnitude * (speed_new_neutron_norm + self.random_unit_vector() * 0.4 )/ 1.4 # to add some noise

                    position_new_neutron = particle.position + speed_new_neutron * simulation_speed # to not interact directly again.
                    new_neutron = Particle(type ="neutron",position = position_new_neutron, speed = speed_new_neutron, mass = self.mass_neutron, radius= self.radius_neutron)
                    new_neutrons.append(new_neutron)
                                        # >>>

                old_uranium = (particle if particle.type == "uranium_235" else possible_neighbour)
                old_uranium.cooldown = -1


                speed_new_barium = -  speed_magnitude_new_products * (speed_new_neutron_norm + self.random_unit_vector() * 0.4 )/1.4 # opposite direction than neutrons + randomness
                speed_new_krypton = - speed_magnitude_new_products * (speed_new_neutron_norm + self.random_unit_vector() * 0.4 )/1.4

                new_barium = Particle(type ="barium",position = old_uranium.position + simulation_speed * speed_new_barium, speed = speed_new_barium, mass = self.mass_barium, radius= self.radius_barium)
                new_krypton = Particle(type ="krypton",position = old_uranium.position + simulation_speed * speed_new_krypton, speed = speed_new_krypton, mass = self.mass_krypton, radius= self.radius_krypton)

                spawned = [new_neutrons , [new_barium], [new_krypton]]
                deleted = old_uranium
                return spawned, deleted

            else:
                # normal interaction
                particle.collision_interact(possible_neighbour)
                return None, None
        else:
            # normal interaction
            particle.collision_interact(possible_neighbour)
            return None, None

    def one_simulation_step(self, particles):
        new_particles = []
        old_particles = []

        for particle in particles:
            for i in range(3):
                if np.abs(particle.position[i]) >bounding_parameter: # bound em by 100x100x100 -> reflect
                    particle.speed[i] *= -1
            particle.forward() # move in space

        # Check each pair once to avoid duplicate/self collision work.-> more efficient and clean <<<
        particle_count = len(particles)
        for i in range(particle_count): # separated from previous loop. bc scaling AND precision.

            particle = particles[i]
            if particle.cooldown == -1: # skip marked (split/removed) particles
                continue

            for j in range(i + 1, particle_count):

                possible_neighbour = particles[j]

                if possible_neighbour.cooldown == -1:  # same principle as above: skip marked (split/removed) particles
                    continue

                if self._check_for_collision(particle, possible_neighbour):
                    spawned, deleted = self._execute_collision_or_interaction(particle, possible_neighbour)
                    if spawned is not None:
                        print (spawned)
                        for particle_category in spawned:
                            new_particles.extend(particle_category)

                    if deleted is not None: # delete the uranium which got split
                        old_particles.append(deleted)

        # >>>
        # kind of what the method returns
        if new_particles:
            particles.extend(new_particles)
        if old_particles:
            for old_particle in old_particles:
                particles.remove(old_particle)

        return len(new_particles), len(old_particles)


    def simulate(self):
        particles = self._innitialize_particles()
        for i in range(self.simulation_steps):
            self.one_simulation_step(particles)



if __name__ == "__main__":
    simulation = Simulation(simulation_steps=10)
    simulation.simulate()
