import argparse
import json
from pathlib import Path

import numpy as np

from parameters import (
    bounding_parameter,
    fission_prob_hardcoded_parameter,
    neutrons_start,
    threshold_factor_uranium,
    uranium_start,
    simulation_steps
)
from simulation import Simulation

TYPES = ("neutron", "uranium_235", "barium", "krypton")


def _create_folder_name(uranium_start_value, neutrons_start_value, bounding_value, fission_prob_value):
    return f"RUN_steps->{simulation_steps}_starting_values_u->{uranium_start_value}_n->{neutrons_start_value}_bound->{bounding_value}_fission_prob->{round(fission_prob_value*100)}"


def _positions_array(positions):
    if not positions:
        return np.empty((0, 3), dtype=np.float32)
    return np.asarray(positions, dtype=np.float32)


def snapshots_to_payload(all_snapshots_positions):
    pos_blocks = {t: [] for t in TYPES}
    offsets = {t: [0] for t in TYPES}

    for snapshot in all_snapshots_positions:
        for t in TYPES:
            arr = _positions_array(snapshot.get(t, []))
            pos_blocks[t].append(arr)
            offsets[t].append(offsets[t][-1] + len(arr))

    payload = {}
    for t in TYPES:
        total = offsets[t][-1]
        if total:
            payload[f"{t}_pos"] = np.concatenate(pos_blocks[t], axis=0)
        else:
            payload[f"{t}_pos"] = np.empty((0, 3), dtype=np.float32)
        payload[f"{t}_offsets"] = np.asarray(offsets[t], dtype=np.int32)

    return payload


def run_and_cache(simulation_steps, uranium_threshold_factor):
    simulator = Simulation(
        simulation_steps=simulation_steps,
        neutrons_start=neutrons_start,
        uranium_start=uranium_start,
    )

    result = simulator.simulate(uranium_threshold=uranium_threshold_factor)
    if result is None:
        print("Simulation stopped early due to uranium threshold; no cache written.")
        return

    all_snapshots_positions, metadata = result

    run_dir = Path(__file__).resolve().parent / run_folder_name(
        uranium_start,
        neutrons_start,
        bounding_parameter,
        fission_prob_hardcoded_parameter,
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = snapshots_to_payload(all_snapshots_positions)
    np.savez_compressed(run_dir / "snapshots.npz", **payload)

    with (run_dir / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    run_config = {
        "simulation_steps": simulation_steps,
        "uranium_threshold_factor": uranium_threshold_factor,
        "uranium_start": uranium_start,
        "neutrons_start": neutrons_start,
        "bounding_parameter": bounding_parameter,
        "fission_prob_hardcoded_parameter": fission_prob_hardcoded_parameter,
    }
    with (run_dir / "run_config.json").open("w", encoding="utf-8") as f:
        json.dump(run_config, f, indent=2)

    print(f"Cached snapshots at {run_dir}")



if __name__ == "__main__":
    run_and_cache(simulation_steps=simulation_steps, uranium_threshold_factor=threshold_factor_uranium)
