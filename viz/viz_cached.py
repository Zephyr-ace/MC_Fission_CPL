import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from core.parameters import (
    bounding_parameter,
    fission_prob_hardcoded_parameter,
    neutrons_start,
    uranium_start,
)

TYPES = ("neutron", "uranium_235", "barium", "krypton")
TYPE_COLORS = {
    "neutron": "#59a14f",
    "uranium_235": "#4c78a8",
    "barium": "#f2c14e",
    "krypton": "#e15759",
}
DEFAULT_COLOR = "#9c9c9c"


def run_dir():
    base_dir = Path(__file__).resolve().parents[1] / "cached_runs"
    return base_dir / (
        f"{uranium_start}_{neutrons_start}_{bounding_parameter}_{fission_prob_hardcoded_parameter}"
    )


def frame_data(npz, frame):
    positions = []
    colors = []
    for t in TYPES:
        offsets = npz[f"{t}_offsets"]
        pos = npz[f"{t}_pos"]
        start, end = offsets[frame], offsets[frame + 1]
        if end > start:
            positions.append(pos[start:end])
            colors.extend([TYPE_COLORS.get(t, DEFAULT_COLOR)] * (end - start))
    if positions:
        return np.vstack(positions), colors
    return np.empty((0, 3), dtype=np.float32), []


def main():
    cache_dir = run_dir()
    if not cache_dir.exists():
        raise SystemExit(f"Cache folder not found: {cache_dir}")

    npz = np.load(cache_dir / "snapshots.npz")
    with (cache_dir / "metadata.json").open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    bounds = bounding_parameter
    config_path = cache_dir / "run_config.json"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        bounds = config.get("bounding_parameter", bounds)

    frames = len(npz[f"{TYPES[0]}_offsets"]) - 1

    pos0, colors0 = frame_data(npz, 0)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    sc = ax.scatter(pos0[:, 0], pos0[:, 1], pos0[:, 2], c=colors0)
    ax.set_xlim(-bounds * 1.1, bounds * 1.1)
    ax.set_ylim(-bounds * 1.1, bounds * 1.1)
    ax.set_zlim(-bounds * 1.1, bounds * 1.1)

    def update(frame):
        pos, colors = frame_data(npz, frame)
        if pos.size == 0:
            sc._offsets3d = ([], [], [])
            sc.set_color([])
        else:
            sc._offsets3d = (pos[:, 0], pos[:, 1], pos[:, 2])
            sc.set_color(colors)
        return sc,

    anim = FuncAnimation(fig, update, frames=frames, interval=50, repeat=False)
    plt.show()

    fig2, ax2 = plt.subplots()
    ax2.plot(metadata.get("neutron_counts", []), label="Neutron", color=TYPE_COLORS["neutron"], linewidth=2)
    ax2.plot(metadata.get("uranium_counts", []), label="Uranium-235", color=TYPE_COLORS["uranium_235"], linewidth=2)
    ax2.plot(metadata.get("barium_counts", []), label="Barium", color=TYPE_COLORS["barium"], linestyle="--")
    ax2.plot(metadata.get("krypton_counts", []), label="Krypton", color=TYPE_COLORS["krypton"], linestyle="--")
    ax2.set_xlabel("Time Step")
    ax2.set_ylabel("Count")
    ax2.set_title("Particle Count Over Time")
    ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95), frameon=False)
    plt.show()


if __name__ == "__main__":
    main()
