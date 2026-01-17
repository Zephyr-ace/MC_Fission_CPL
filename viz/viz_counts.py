import json
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    folder = input("cached_runs group folder: ").strip()
    if not folder:
        raise SystemExit("No folder provided.")

    cache_dir = Path(__file__).resolve().parents[1] / "cached_runs" / folder
    if not cache_dir.exists():
        raise SystemExit(f"Cache folder not found: {cache_dir}")

    fig, ax = plt.subplots()
    metadata_path = cache_dir / "metadata.json"
    if metadata_path.exists():
        with metadata_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
        ax.plot(metadata.get("uranium_counts", []), label="Uranium-235")
        ax.plot(metadata.get("neutron_counts", []), label="Neutron")
    else:
        runs = [p for p in cache_dir.iterdir() if (p / "metadata.json").exists()]
        if not runs:
            raise SystemExit(f"No metadata.json files found in: {cache_dir}")
        runs.sort(key=lambda p: p.name)
        for i, run_dir in enumerate(runs):
            with (run_dir / "metadata.json").open("r", encoding="utf-8") as f:
                metadata = json.load(f)
            uranium = metadata.get("uranium_counts", [])
            neutron = metadata.get("neutron_counts", [])
            ax.plot(uranium, color="tab:blue", alpha=0.3, label="Uranium-235" if i == 0 else None)
            ax.plot(neutron, color="tab:orange", alpha=0.3, label="Neutron" if i == 0 else None)
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Count")
    ax.set_title(f"Counts Over Time: {folder}")
    ax.legend(frameon=False)
    plt.show()


if __name__ == "__main__":
    main()
