"""
Phase 1 of the Model Monitor lab: synthetic credit-default data.

Run from the repo root (genai-portfolio/):  python3 gen_data.py
Writes six CSVs into monitor_lab/data/. Same seed -> same files every run.

File shapes (this is the part that matters for SageMaker):
  train.csv / validation.csv : label FIRST, NO header   -> training job
  baseline.csv               : features only, HEADER    -> Model Monitor baseline
  traffic_*.csv              : features only, NO header -> rows we send to the endpoint
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
OUT_DIR = Path("monitor_lab/data")
# Column ORDER matters: the endpoint reads by position, Model Monitor matches by position.
FEATURES = [
    "age", "income", "loan_amount", "credit_score",
    "employment_years", "utilization", "delinquencies", "account_age",
]

rng = np.random.default_rng(SEED)


def make_features(n, drifted=False):
    """Draw n borrowers. drifted=True shifts four features: credit_score, utilization, income, loan_amount."""
    age = np.clip(rng.normal(40, 10, n), 18, 80)
    income = rng.lognormal(10.8, 0.4, n)                      # right-skewed, always > 0
    loan_amount = income * rng.uniform(0.1, 0.6, n)           # correlated with income
    credit_score = np.clip(rng.normal(600 if drifted else 680, 60, n), 300, 850)
    employment_years = np.minimum(rng.gamma(2.0, 3.0, n), age - 18)
    utilization = np.clip(rng.beta(3, 3, n) if drifted else rng.beta(2, 5, n), 0, 1)
    delinquencies = rng.poisson(0.3, n)
    account_age = np.minimum(rng.gamma(3.0, 2.5, n), age - 18)

    if drifted:                                               # incomes rose
        income = income * 1.35
        loan_amount = loan_amount * 1.35

    # Round AFTER drifting so every file has the same column types
    # (Model Monitor infers Integral vs Fractional per column from the baseline).
    return pd.DataFrame({
        "age": age.round().astype(int),
        "income": income.round().astype(int),
        "loan_amount": loan_amount.round().astype(int),
        "credit_score": credit_score.round().astype(int),
        "employment_years": employment_years.round(1),
        "utilization": utilization.round(3),
        "delinquencies": delinquencies.astype(int),
        "account_age": account_age.round(1),
    })


def make_labels(df):
    """1 = defaulted. Probability comes from the features, plus randomness."""
    z = (-2.2
         + 2.0 * df["utilization"]
         + 0.55 * df["delinquencies"]
         - 0.9 * (df["credit_score"] - 680) / 60
         + 1.5 * (df["loan_amount"] / df["income"])
         - 0.03 * df["employment_years"])
    p = 1 / (1 + np.exp(-z))
    return rng.binomial(1, p)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train = make_features(5000)
    train["label"] = make_labels(train)
    valid = make_features(1000)
    valid["label"] = make_labels(valid)

    normal = make_features(600)                   # same distribution as training
    drifted = make_features(600, drifted=True)    # distribution shift (reliable drift)

    malformed = make_features(30)                 # best-effort: endpoint may reject these
    malformed.loc[:14, "employment_years"] = np.nan   # 15 rows with a missing value
    malformed.loc[15:, "age"] = 250                   # 15 rows with an impossible age

    label_first = ["label"] + FEATURES
    train[label_first].to_csv(OUT_DIR / "train.csv", header=False, index=False)
    valid[label_first].to_csv(OUT_DIR / "validation.csv", header=False, index=False)
    train[FEATURES].to_csv(OUT_DIR / "baseline.csv", header=True, index=False)
    for name, frame in [("traffic_normal", normal),
                        ("traffic_drifted", drifted),
                        ("traffic_malformed", malformed)]:
        frame[FEATURES].to_csv(OUT_DIR / f"{name}.csv", header=False, index=False)

    print(f"train: {train.shape}  default rate: {train['label'].mean():.3f}")
    print(f"validation: {valid.shape}  default rate: {valid['label'].mean():.3f}")
    print("\nFeature means (baseline vs live traffic):")
    print(pd.DataFrame({
        "baseline": train[FEATURES].mean(),
        "normal": normal[FEATURES].mean(),
        "drifted": drifted[FEATURES].mean(),
    }).round(2))
    print(f"\nFiles written to {OUT_DIR}/")


if __name__ == "__main__":
    main()