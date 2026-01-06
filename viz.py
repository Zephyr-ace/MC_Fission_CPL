import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simulation import Simulation

simulator = Simulation(simulation_steps=200, neutrons_start=50, uranium_start=50)
particles = simulator._innitialize_particles()

def positions_from_particles(particles):
    if not particles:
        print("hmm weird")
        return np.empty((0, 3), dtype=np.float64)

    return np.array([p.position for p in particles], dtype=np.float64)

pos = positions_from_particles(particles)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

sc = ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2])
ax.set_xlim(0, 120)
ax.set_ylim(0, 120)
ax.set_zlim(0, 120)

def update(frame):
    simulator.one_simulation_step(particles)
    pos = positions_from_particles(particles)
    if pos.size == 0:
        sc._offsets3d = ([], [], [])
    else:
        sc._offsets3d = (pos[:, 0], pos[:, 1], pos[:, 2])
    return sc,

ani = FuncAnimation(fig, update, frames=simulator.simulation_steps, interval=50)
plt.show()
