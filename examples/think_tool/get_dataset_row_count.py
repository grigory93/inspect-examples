import os
from inspect_evals.gaia.dataset import gaia_dataset

def main():
    levels = ["2023_level1", "2023_level2", "2023_level3", "2023_all"]
    splits = ["validation"] 

    print(f"{'Subset':<15} | {'Split':<10} | {'Count':<5}")
    print("-" * 35)

    for level in levels:
        for split in splits:
            try:
                # Suppress some HF warnings if possible, or just run
                dataset = gaia_dataset(subset=level, split=split)
                print(f"{level:<15} | {split:<10} | {len(dataset):<5}")
            except Exception as e:
                print(f"{level:<15} | {split:<10} | Error: {e}")
                if "HF_TOKEN" in str(e) or "401" in str(e):
                    print("  (Ensure HF_TOKEN is set and you have access to the GAIA dataset on HuggingFace)")

if __name__ == "__main__":
    main()

