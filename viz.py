import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simulation import Simulation
from parameters import threshold_factor_uranium, bounding_parameter

simulator = Simulation(simulation_steps=10**8, neutrons_start=1, uranium_start=200)
particles = simulator._innitialize_particles()

TYPE_COLORS = {
    "neutron": "#59a14f",
    "uranium_235": "#4c78a8",
    "barium": "#f2c14e",
    "krypton": "#e15759",
}
DEFAULT_COLOR = "#9c9c9c"

def positions_from_particles(particles):
    if not particles:
        print("hmm weird")
        return np.empty((0, 3), dtype=np.float64)

    return np.array([p.position for p in particles], dtype=np.float64)

def colors_from_particles(particles):
    return [TYPE_COLORS.get(p.type, DEFAULT_COLOR) for p in particles]

pos = positions_from_particles(particles)
colors = colors_from_particles(particles)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

fig.subplots_adjust(bottom=0.1)
progress_ax = fig.add_axes([0.15, 0.03, 0.7, 0.03])
progress_ax.set_xlim(0, 1)
progress_ax.set_ylim(0, 1)
progress_ax.axis("off")
progress_bar = progress_ax.barh(0.5, 0.0, height=1.0, color="#3a7bd5")[0]
progress_text = progress_ax.text(0.5, 0.5, "0%", ha="center", va="center",
                                 color="white", fontsize=9)

sc = ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], c=colors)
ax.set_xlim(-bounding_parameter * 1.1, bounding_parameter * 1.1)
ax.set_ylim(-bounding_parameter * 1.1, bounding_parameter * 1.1)
ax.set_zlim(-bounding_parameter * 1.1, bounding_parameter * 1.1)

neutron_count = [simulator.neutrons_start]
uranium_count = [simulator.uranium_start]

uranium_threshold = simulator.uranium_start * threshold_factor_uranium

def update(frame):

    n_new_neutrons, n_old_uranium = simulator.one_simulation_step(particles) # modifies particles directly, outputs metadata
    neutron_count.append(neutron_count[-1] + n_new_neutrons)
    uranium_count.append(uranium_count[-1] - n_old_uranium)

    pos = positions_from_particles(particles)
    colors = colors_from_particles(particles)
    if pos.size == 0:
        sc._offsets3d = ([], [], [])
        sc.set_color([])
    else:
        sc._offsets3d = (pos[:, 0], pos[:, 1], pos[:, 2])
        sc.set_color(colors)
    progress = (frame + 1) / simulator.simulation_steps
    progress_bar.set_width(progress)
    progress_text.set_text(f"{progress * 100:.0f}%")

    if uranium_count[-1] <= uranium_threshold:
        progress_bar.set_width(1.0)
        progress_text.set_text("100%")
        ani.event_source.stop()

    return sc, progress_bar, progress_text

ani = FuncAnimation(fig, update, frames=simulator.simulation_steps, interval=50, repeat = False)
plt.show()



# After the FuncAnimation is done, create a new figure for the count plot
fig2, ax2 = plt.subplots()
ax2.plot(range(len(neutron_count)), neutron_count, label='Neutron Count')
ax2.plot(range(len(uranium_count)), uranium_count, label='Uranium Count')
ax2.set_xlabel('Time Step')
ax2.set_ylabel('Count')
ax2.set_title('Particle Count Over Time')
ax2.legend()

plt.show()
