"""
Local replacement for SageMaker Model Monitor (closed to new AWS accounts
as of 7/30/26). Same job, no endpoint, no waiting for an hourly schedule.

Compares monitor_lab/data/baseline.csv (what training data looked like)
against traffic_normal.csv and traffic_drifted.csv (what "live" data
looks like), one HTML report per comparison.

Run from the repo root:  python3 run_drift_report.py
"""
from pathlib import Path
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

DATA_DIR = Path("monitor_lab/data")
OUT_DIR = Path("monitor_lab/reports")
FEATURES = [
    "age", "income", "loan_amount", "credit_score",
    "employment_years", "utilization", "delinquencies", "account_age",
]


def run_one(baseline, traffic, out_name):
    ref = pd.read_csv(baseline)
    cur = pd.read_csv(traffic, header=None, names=FEATURES)  # traffic files have no header - name them here
    report = Report([DataDriftPreset()])
    result = report.run(reference_data=ref, current_data=cur)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / out_name
    result.save_html(str(out_path))
    print(f"{out_name} written -> {out_path}")

    # metric_results is a dict keyed by an internal id; each value carries
    # the real column name and threshold under .metric_value_location.metric.params
    print(f"  {'column':20s} {'distance':>10s} {'threshold':>10s}  status")
    for entry in result.metric_results.values():
        cfg = entry.metric_value_location.metric
        col = cfg.params.get("column")
        if not col:
            continue  # skip the dataset-level "Count of Drifted Columns" entry
        threshold = cfg.params.get("threshold")
        value = entry.value
        flag = "DRIFTED" if (threshold is not None and value is not None and value > threshold) else "ok"
        print(f"  {col:20s} {value:10.4f} {threshold:10.2f}  {flag}")
    return result


if __name__ == "__main__":
    print("Comparing baseline vs NORMAL traffic (expect: little to no drift)")
    run_one(DATA_DIR / "baseline.csv", DATA_DIR / "traffic_normal.csv", "report_normal.html")

    print("\nComparing baseline vs DRIFTED traffic (expect: drift on income, "
          "loan_amount, credit_score, utilization)")
    run_one(DATA_DIR / "baseline.csv", DATA_DIR / "traffic_drifted.csv", "report_drifted.html")