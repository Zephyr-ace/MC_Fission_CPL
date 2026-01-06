import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

pos = np.random.randn(5, 3)  # start with 5 particles


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


# viz settings
sc = ax.scatter(pos[:,0], pos[:,1], pos[:,2])
ax.set_xlim(-5, 5); ax.set_ylim(-5, 5); ax.set_zlim(-5, 5)

def update(frame):
    global pos, sc

    # add a particle at frame 50
    if frame == 50:
        new_particle = np.array([[0.0, 0.0, 0.0]])
        pos = np.vstack([pos, new_particle])

    # motion update
    pos += 0.05*np.random.randn(*pos.shape)

    # update scatter data
    sc._offsets3d = (pos[:,0], pos[:,1], pos[:,2])
    return sc,

ani = FuncAnimation(fig, update, frames=200, interval=50)
plt.show()
