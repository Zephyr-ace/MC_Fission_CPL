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



# <<<<<<<<<<<<<<<<<<< visualization
# Set up Plotly figure for 3D visualization
fig = go.Figure(data=[go.Scatter3d(
    x=[p.position[0] for p in particles],
    y=[p.position[1] for p in particles],
    z=[p.position[2] for p in particles],
    mode='markers', marker=dict(size=5)
)])

# Update layout for axes labels
fig.update_layout(scene=dict(
    xaxis_title='X',
    yaxis_title='Y',
    zaxis_title='Z'
))
# Show the plot
fig.show()




for i in range(10):
    for particle in particles:
        print("before", particle.position)
        particle.forward()
        print("after", particle.position)

        # <<<<< visualization
        # Update particle positions in Plotly figure
        fig.data[0].update(
            x=[p.position[0] for p in particles],
            y=[p.position[1] for p in particles],
            z=[p.position[2] for p in particles]
        )

        fig.update()  # Redraw the plot with new data
        time.sleep(0.1)  # Simulate delay for real-time updates
