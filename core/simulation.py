from core.particles import Particle, simulation_speed
import numpy as np
import random
from core.parameters import sigma_0, sigma_thermal, E_0, alpha, bounding_parameter, neutron_speed_magnitude, \
    radius_multiplicator,simulation_steps, neutron_init_speed, fission_prob_hardcoded_parameter, speed_magnitude_new_products, uranium_start, neutrons_start, threshold_factor_uranium

class Simulation:

    def __init__(self, simulation_steps, neutrons_start, uranium_start,
                 bounding_parameter=bounding_parameter,
                 fission_prob_hardcoded_parameter=fission_prob_hardcoded_parameter):
        self.simulation_steps = simulation_steps
        self.neutrons_start = neutrons_start
        self.uranium_start = uranium_start
        self.bounding_parameter = bounding_parameter
        self.fission_prob_hardcoded_parameter = fission_prob_hardcoded_parameter

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
            position_vector = np.random.uniform(low = -self.bounding_parameter*0.9, high= self.bounding_parameter*0.9, size=3)
            particles.append(Particle("neutron", speed_vector, position_vector, self.mass_neutron, self.radius_neutron))


        # instance particle objects of type uranium
        for i in range(self.uranium_start):
            speed_mag = np.random.uniform(0, 100)
            speed_vector = self.random_unit_vector() * speed_mag
            position_vector = np.random.uniform(-self.bounding_parameter*0.9, self.bounding_parameter*0.9, 3)
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
            if self.fission_prob_hardcoded_parameter is not None:
                fission_prob = self.fission_prob_hardcoded_parameter # for the simulation to work with fewer particles.

            if random.random() < fission_prob:

                # create 2-3 new neutrons <<<
                a = 2
                if random.random() < 0.5:
                    a = 3

                new_neutrons = []
                speed_new_neutron_direction = np.cross(particle.speed, possible_neighbour.speed)  # won't interfere with either of other particles
                speed_new_neutron_direction_norm = np.linalg.norm(speed_new_neutron_direction)
                if speed_new_neutron_direction_norm == 0:
                    speed_new_neutron_norm = self.random_unit_vector()
                else:
                    speed_new_neutron_norm = speed_new_neutron_direction / speed_new_neutron_direction_norm

                for i in range(a):
                    speed_new_neutron = neutron_speed_magnitude * (speed_new_neutron_norm + self.random_unit_vector() * 0.4 )/ 1.4 # to add some noise

                    position_new_neutron = particle.position + speed_new_neutron * simulation_speed # to not interact directly again.
                    new_neutron = Particle(type ="neutron",position = position_new_neutron, speed = speed_new_neutron, mass = self.mass_neutron, radius= self.radius_neutron)
                    new_neutrons.append(new_neutron)
                                        # >>>

                old_uranium = (particle if particle.type == "uranium_235" else possible_neighbour)
                old_uranium.cooldown = -1


                product_dir = speed_new_neutron_norm + self.random_unit_vector() * 0.4
                speed_new_barium = -speed_magnitude_new_products * product_dir / 1.4 # opposite directions + randomness
                speed_new_krypton = speed_magnitude_new_products * product_dir / 1.4

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

    def one_simulation_step(self, particles, metadata):
        new_particles = []
        old_particles = []

        for particle in particles:
            particle.forward() # move in space
            for i in range(3):
                if particle.position[i] > self.bounding_parameter: # reflect and clamp
                    particle.position[i] = self.bounding_parameter
                    particle.speed[i] *= -1
                elif particle.position[i] < -self.bounding_parameter:
                    particle.position[i] = -self.bounding_parameter
                    particle.speed[i] *= -1

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
                        for spawned_group in spawned:
                            new_particles.extend(spawned_group)

                    if deleted is not None: # delete the uranium which got split
                        old_particles.append(deleted)

        # >>>
        # kind of what the method returns
        if new_particles:
            particles.extend(new_particles)

        if old_particles:
            for old_particle in old_particles:
                particles.remove(old_particle)

        # metadata counts (recompute by type to avoid mixing products)
        counts = {"neutron": 0, "uranium_235": 0, "barium": 0, "krypton": 0}
        for particle in particles:
            if particle.cooldown == -1:
                continue
            counts[particle.type] += 1

        metadata["neutron_counts"].append(counts["neutron"])
        metadata["uranium_counts"].append(counts["uranium_235"])
        metadata["barium_counts"].append(counts["barium"])
        metadata["krypton_counts"].append(counts["krypton"])

        return particles, metadata

    def _snapshot_particles(self, particles):
        snapshot_positions = {"neutron": [], "uranium_235": [], "barium": [], "krypton": []}
        for particle in particles:
            snapshot_positions[particle.type].append(particle.position.copy()) # copy () fixes mutable bug
        return snapshot_positions


    def simulate(self, uranium_threshold = 0.0):
        particles = self._innitialize_particles()
        metadata = {
            "uranium_counts": [self.uranium_start],
            "neutron_counts": [self.neutrons_start],
            "barium_counts": [0],
            "krypton_counts": [0],
        }
        all_snapshots_positions = []

        for i in range(self.simulation_steps):
            self.one_simulation_step(particles, metadata)  # modifies particles and metadata directly
            all_snapshots_positions.append(self._snapshot_particles(particles)) # save snapshot of positions

            # check if uranium bellow treshold
            if metadata["uranium_counts"][-1] <= uranium_threshold * metadata["uranium_counts"][0]:
                return all_snapshots_positions, metadata

        return all_snapshots_positions, metadata

def run_multiple_monte_carlo(simulation_steps=simulation_steps,
                             uranium_threshold_factor=threshold_factor_uranium,
                             bounding_parameters=None,
                             fission_probabilities=None):

    if bounding_parameters is None:
        bounding_parameters = [bounding_parameter]
    if fission_probabilities is None:
        fission_probabilities = [fission_prob_hardcoded_parameter]

    from core.run_and_cache import run_and_cache

    for bound in bounding_parameters:
        for fission_prob in fission_probabilities:
            run_and_cache(
                simulation_steps,
                uranium_threshold_factor,
                bounding_parameter=bound,
                fission_prob_hardcoded_parameter=fission_prob,
            )


if __name__ == "__main__":
    simulation = Simulation(simulation_steps=simulation_steps, uranium_start=uranium_start, neutrons_start=neutrons_start)
    s, m = simulation.simulate()
    for snapshot in s:
        print(snapshot)
