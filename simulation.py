from particles import Particle
import numpy as np
import plotly.graph_objects as go
import time
import random

collision_distance = 100

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
    return probability

def simulate (simulation_steps, neutrons_start: int = 10, uranium_start: int = 10):

    particles = []

    # instance particle objects of type neutron
    for i in range(neutrons_start):
        speed_vector = np.random.randint(0, 5000, 3)
        position_vector = np.random.randint(0, 100, 3)
        mass_neutron = 1.675 * 10**-27

        particles.append(Particle("neutron", speed_vector, position_vector, mass_neutron))

    # instance particle objects of type uranium
    for i in range(uranium_start):
        speed_vector = np.random.randint(0, 1, 3)
        position_vector = np.random.randint(0, 100, 3)
        mass_uranium_235 = 3.91 * 10**-25

        particles.append(Particle("uranium_235", speed_vector, position_vector, mass_uranium_235))


    for i in range(10):
        for particle in particles:
            particle.forward()
            for possible_neighbor in particles: # check for collisions with ALL other particles (very inefficient and bad scaling ik=)
                if particle.cooldown < 1 and possible_neighbor.cooldown < 1: # both havent just interacted, to avoid endless interactions
                    distance = particle.distance(possible_neighbor)
                    print(distance)
                    if distance <= collision_distance and distance != -1.0 : # if two particles are very close but NOT the same particle -> interaction

                        # checking for fission possibility
                        if (particle.type == "uranium_235" and possible_neighbor.type == "neutron") or (particle.type == "neutron" and possible_neighbor.type == "uranium_235"):
                            if random.random() < fission_probability(particle.speed, possible_neighbor.speed):
                                print("fission")
                        else:
                            particle.collision_interact(possible_neighbor)







simulate(100, 1000, 100)