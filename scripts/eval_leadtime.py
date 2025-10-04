"""
Evaluate lead-time detection: compute metrics, top-5 table, histogram.
"""

# Force non-interactive backend for headless environments
import matplotlib
matplotlib.use('Agg')

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description="Evaluate lead-time detection performance")
    parser.add_argument(
        "--summary",
        default="anomaly_summary.csv",
        help="Path to anomaly_summary.csv"
    )
    parser.add_argument(
        "--outdir",
        default="outputs",
        help="Directory to write metrics and plots"
    )
    args = parser.parse_args()

    # Resolve to absolute paths
    input_file = Path(args.summary).resolve()
    output_dir = Path(args.outdir).resolve()
    
    print(f"Loading {input_file}...")
    print(f"Output directory: {output_dir}")

    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check input file exists
        if not input_file.exists():
            raise FileNotFoundError(f"Summary file not found: {input_file}")

        # Load data
        df = pd.read_csv(input_file)

        # Basic validation
        required_cols = {"battery_id", "lead_cycles", "total_cycles"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Missing required columns. Expected: {required_cols}")

        # Compute metrics
        total_cells = len(df)
        cells_with_anomalies = (df["lead_cycles"] > 0).sum()
        mean_lead = df.loc[df["lead_cycles"] > 0, "lead_cycles"].mean()
        median_lead = df.loc[df["lead_cycles"] > 0, "lead_cycles"].median()

        metrics = {
            "cells": int(total_cells),  
            "cells_with_anomalies": int(cells_with_anomalies),
            "mean_lead_cycles": float(mean_lead) if pd.notna(mean_lead) else 0.0,
            "median_lead_cycles": float(median_lead) if pd.notna(median_lead) else 0.0,
        }

        # Save metrics JSON
        metrics_path = output_dir / "lead_time_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"Saved metrics to {metrics_path}")

        # Build top-5 table
        top5 = df.nlargest(5, "lead_cycles")[
            ["battery_id", "lead_cycles", "first_anomaly_test_id", "eol_test_id", "total_cycles"]
        ].copy()

        # Cast to int where appropriate (prevents 6.0, 42.0 formatting)
        int_columns = ["battery_id", "lead_cycles", "first_anomaly_test_id", "eol_test_id", "total_cycles"]
        for col in int_columns:
            if col in top5.columns:
                # Only convert if all values are whole numbers (not NaN)
                if top5[col].notna().all():
                    top5[col] = top5[col].astype(int)

        top5_path = output_dir / "lead_time_top5.csv"
        top5.to_csv(top5_path, index=False)
        print(f"Saved top-5 lead times to {top5_path}")

        # Plot histogram
        lead_data = df.loc[df["lead_cycles"] > 0, "lead_cycles"]
        if len(lead_data) > 0:
            plt.figure(figsize=(8, 5))
            plt.hist(lead_data, bins=20, edgecolor="black", alpha=0.7)
            plt.xlabel("Lead Cycles")
            plt.ylabel("Frequency")
            plt.title("Distribution of Lead-Time (Cycles Before EOL)")
            plt.grid(axis="y", alpha=0.3)
            
            hist_path = output_dir / "lead_time_histogram.png"
            plt.savefig(hist_path, dpi=150, bbox_inches="tight")
            plt.close()
            print(f"Saved histogram to {hist_path}")
        else:
            print("No anomalies detected; skipping histogram.")

        print("\nMetrics summary:")
        print(f"  Total cells: {metrics['cells']}")
        print(f"  Cells with anomalies: {metrics['cells_with_anomalies']}")
        print(f"  Mean lead cycles: {metrics['mean_lead_cycles']:.1f}")
        print(f"  Median lead cycles: {metrics['median_lead_cycles']:.1f}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())