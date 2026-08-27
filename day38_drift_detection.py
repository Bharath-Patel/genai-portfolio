import json
import os
from datetime import datetime
from day37_eval_gate import run_eval

BASELINE_FILE = "eval_baseline.json"

def save_baseline():
    result = run_eval()
    df = result.to_pandas()

    baseline = {
        "timestamp" : datetime.now().isoformat(),
        "avg_faithfulness" : float(df["faithfulness"].mean()),
        "avg_context_precision" : float(df["context_precision"].mean()),
        "perr_question_faithfulness" : df["faithfulness"].tolist()
    }

    with open(BASELINE_FILE,"w") as f:
        json.dump(baseline,f, indent =2)

    print(f"Baseline saved: with faithfulness={baseline['avg_faithfulness']:.3f}, "
          f"context_precision={baseline['avg_context_precision']:.3f}")
    return baseline

def check_against_baseline(drift_tolerance:float = 0.1):
    if not os.path.exists(BASELINE_FILE):
        print("No baseline found: run with --save-baseline  first")
        return

    with open(BASELINE_FILE,"r") as f:
        baseline = json.load(f)

    result = run_eval()
    df = result.to_pandas()
    current_faithfulness = float(df["faithfulness"].mean())
    current_context_precision = float(df["context_precision"].mean())
    print(f"Baseline faithfulness: {baseline['avg_faithfulness']:.3f}")
    print(f"Current faithfulness:  {current_faithfulness:.3f}")

    faithfulness_drop = baseline["avg_faithfulness"] - current_faithfulness

    if faithfulness_drop > drift_tolerance:
        print(f"Drift detected: with drop in faitfulness by {faithfulness_drop:.3f}")
        return False
    else:
        print(f"No significant drift (change: {faithfulness_drop:.3f})")
        return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--save-baseline":
        save_baseline()
    else:
        check_against_baseline()