import json
from pathlib import Path

import numpy as np

from logic.parameters import (
    bounding_parameter,
    fission_prob_hardcoded_parameter,
    neutrons_start,
    threshold_factor_uranium,
    uranium_start,
    simulation_steps,
)

from logic.simulation import Simulation

TYPES = ("neutron", "uranium_235", "barium", "krypton")

def _create_folder_name():
    dir_name = Path(__file__).resolve().parent / (f"{uranium_start}_{neutrons_start}_{bounding_parameter}_{fission_prob_hardcoded_parameter}")
    return dir_name

def run_and_cache(simulation_steps=simulation_steps, uranium_threshold_factor=threshold_factor_uranium):
    simulator = Simulation(
        simulation_steps=simulation_steps,
        neutrons_start=neutrons_start,
        uranium_start=uranium_start,
    )


    snapshots, metadata = simulator.simulate(uranium_threshold=uranium_threshold_factor)

    dir_name = _create_folder_name()
    dir_name.mkdir(parents=True, exist_ok=True) # create dir

    pos_blocks = {t: [] for t in TYPES}
    offsets = {t: [0] for t in TYPES} # caching start/end of each snapshot

    for snapshot in snapshots:
        for t in TYPES:
            arr = np.asarray(snapshot.get(t, []), dtype=np.float32)
            pos_blocks[t].append(arr)
            offsets[t].append(offsets[t][-1] + len(arr)) # caching start/end of each snapshot


    payload = {}
    for t in TYPES:
        if offsets[t][-1]:
            payload[f"{t}_pos"] = np.concatenate(pos_blocks[t], axis=0)
        else:
            payload[f"{t}_pos"] = np.empty((0, 3), dtype=np.float32)
        payload[f"{t}_offsets"] = np.asarray(offsets[t], dtype=np.int32)

    np.savez_compressed(dir_name / "snapshots.npz", **payload)
    with (dir_name / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f)

    print(f"Cached snapshots at {dir_name}")


if __name__ == "__main__":
    run_and_cache()
