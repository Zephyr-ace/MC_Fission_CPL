from particles import Particle
import numpy as np
import plotly.graph_objects as go
import time


particles = []

for i in range(10):
    speed_vector = np.random.randint(0, 10, 3)
    position_vector = np.random.randint(0, 100, 3)
    mass_neutron = 1.675 * 10**-27
    particles.append(Particle("neutron", speed_vector, position_vector, mass_neutron))



for i in range(10):
    for particle in particles:
        print("before", particle.position)
        particle.forward()
        print("after", particle.position)
