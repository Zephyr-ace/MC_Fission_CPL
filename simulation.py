from particles import Particle
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

def fission_probability(v1,v2):
    v = np.linalg.norm(v1 - v2) # speed difference
    probability = (sigma_0 / sigma_thermal) * (5.22e-2 * v**2 / E_0)**(-alpha)
    if probability > 1:
        print("Error in code, probablity > 1 !!!")
    return probability, v

def simulate (simulation_steps, neutrons_start: int = 10, uranium_start: int = 10):

    particles = []

    # instance particle objects of type neutron
    for i in range(neutrons_start):
        speed_vector = np.random.randint(2000, 2200, 3)
        position_vector = np.random.randint(0, 30, 3)
        mass_neutron = 1.675 * 10**-27
        radius_neutron = 8 * 10**-16

        particles.append(Particle("neutron", speed_vector, position_vector, mass_neutron, radius_neutron))
    print(f"created {neutrons_start} neutron particles")

    # instance particle objects of type uranium
    for i in range(uranium_start):
        speed_vector = np.random.randint(0, 1, 3)
        position_vector = np.random.randint(0, 100, 3)
        mass_uranium_235 = 3.91 * 10**-25
        radius_uranium = 1.5 * 10

        particles.append(Particle("uranium_235", speed_vector, position_vector, mass_uranium_235, radius_uranium))
    print(f"created {uranium_start} Uranium particles")

    stats = []
    for i in range(simulation_steps):

        fission_count = 0
        stats.append((i,fission_count))

        print("="*10)
        print("steps: ", i, "number of fissions: ", fission_count)
        print("="*10)

        for particle in particles:
            particle.forward()
            for possible_neighbor in particles: # check for collisions with ALL other particles (very inefficient and bad scaling ik=)
                #if particle.id == particles[0].id:
                #    print(particle.type, possible_neighbor.type, particle.cooldown, possible_neighbor.cooldown)

                if particle.cooldown == 0 and possible_neighbor.cooldown == 0: # both havent just interacted, to avoid endless interactions

                    distance = particle.distance(possible_neighbor)

                    collision_distance = particle.radius + possible_neighbor.radius

                    if distance <= collision_distance and distance != -1.0 : # if two particles are very close but NOT the same particle -> interaction

                        # checking for fission possibility
                        if (particle.type == "uranium_235" and possible_neighbor.type == "neutron") or (particle.type == "neutron" and possible_neighbor.type == "uranium_235"):
                            fission_prob, v = fission_probability(particle.speed, possible_neighbor.speed)
                            fission_prob = 1
                            print("fission_probability:     ", fission_prob, v)

                            if random.random() < fission_prob:
                                print("fission!!! wow!")
                                particles.append(Particle("neutron", speed_vector, position_vector, mass_neutron, radius_neutron))
                                print("neutron has been created!")
                                fission_count += 1

                            else:
                                # normal interaction
                                print(particle.type, possible_neighbor.type)
                                v = np.linalg.norm(particle.speed - possible_neighbor.speed)
                                print("interaction but not fission, speed:   ", v)

                                particle.collision_interact(possible_neighbor)
                        else:
                            # normal interaction
                            particle.collision_interact(possible_neighbor)
    return stats






stats = simulate(100, 100, 100)
print("="*100)
print (stats)