import json
from pathlib import Path

import numpy as np

from core.parameters import (
    bounding_parameter,
    fission_prob_hardcoded_parameter,
    neutrons_start,
    threshold_factor_uranium,
    uranium_start,
    simulation_steps,
)

from core.simulation import Simulation

TYPES = ("neutron", "uranium_235", "barium", "krypton")

def _create_folder_name(bounding_parameter_value, fission_prob_hardcoded_parameter_value, base_dir=None):
    base_dir = Path(base_dir) if base_dir is not None else Path(__file__).resolve().parents[1] / "cached_runs"
    return base_dir / (
        f"{uranium_start}_{neutrons_start}_{bounding_parameter_value}_{fission_prob_hardcoded_parameter_value}"
    )

def run_and_cache(simulation_steps, uranium_threshold_factor,
                  bounding_parameter=bounding_parameter,
                  fission_prob_hardcoded_parameter=fission_prob_hardcoded_parameter,
                  base_cache_dir=None):
    simulator = Simulation(simulation_steps, neutrons_start, uranium_start,
                           bounding_parameter=bounding_parameter,
                           fission_prob_hardcoded_parameter=fission_prob_hardcoded_parameter)

    snapshots, metadata = simulator.simulate(uranium_threshold=uranium_threshold_factor)

    dir_name = _create_folder_name(bounding_parameter, fission_prob_hardcoded_parameter, base_dir=base_cache_dir)
    dir_name.mkdir(parents=True, exist_ok=True) # create dir

    pos_blocks = {t: [] for t in TYPES} # dict containing lists of snapshots (in np array format)
    offsets = {t: [0] for t in TYPES} # caching start/end of each snapshot

    for snapshot in snapshots:
        for t in TYPES:
            arr = np.asarray(snapshot.get(t, []), dtype=np.float32)
            if arr.size == 0:
                arr = np.empty((0, 3), dtype=np.float32)
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




    # cache parameters as json
    run_config = {
        "simulation_steps": simulation_steps,
        "uranium_threshold_factor": uranium_threshold_factor,
        "uranium_start": uranium_start,
        "neutrons_start": neutrons_start,
        "bounding_parameter": bounding_parameter,
        "fission_prob_hardcoded_parameter": fission_prob_hardcoded_parameter,
    }
    with (dir_name / "run_config.json").open("w", encoding="utf-8") as f:
        json.dump(run_config, f)

    print(f"Cached snapshots at {dir_name}")


def run_multiple_monte_carlo(simulation_steps=simulation_steps,
                             uranium_threshold_factor=threshold_factor_uranium,
                             bounding_parameters=None,
                             fission_probabilities=None):
    if bounding_parameters is None:
        bounding_parameters = [bounding_parameter]
    if fission_probabilities is None:
        fission_probabilities = [fission_prob_hardcoded_parameter]

    base_dir = Path(__file__).resolve().parents[1] / "cached_runs"
    multiple_bounding = len(bounding_parameters) > 1
    multiple_fission = len(fission_probabilities) > 1

    if multiple_bounding:
        base_cache_dir = base_dir / "bounding_parameter"
        for bound in bounding_parameters:
            run_and_cache(
                simulation_steps,
                uranium_threshold_factor,
                bounding_parameter=bound,
                fission_prob_hardcoded_parameter=fission_probabilities[0],
                base_cache_dir=base_cache_dir,
            )

    if multiple_fission:
        base_cache_dir = base_dir / "fission_prob_hardcoded_parameter"
        for fission_prob in fission_probabilities:
            run_and_cache(
                simulation_steps,
                uranium_threshold_factor,
                bounding_parameter=bounding_parameters[0],
                fission_prob_hardcoded_parameter=fission_prob,
                base_cache_dir=base_cache_dir,
            )

    if not multiple_bounding and not multiple_fission:
        run_and_cache(
            simulation_steps,
            uranium_threshold_factor,
            bounding_parameter=bounding_parameters[0],
            fission_prob_hardcoded_parameter=fission_probabilities[0],
            base_cache_dir=base_dir,
        )


if __name__ == "__main__":
    run_multiple_monte_carlo(
                             bounding_parameters=[4,6,8,10,12,15,20,30,45,60,100],
                             fission_probabilities=[0.01,0.05,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],)