"""Make practice review files for BatchPipe.

Usage (from the project folder):
    python tools/make_data.py 100            -> data/reviews_100.csv
    python tools/make_data.py 1m             -> data/reviews_1m.csv  (1,000,000 rows)
    python tools/make_data.py 1000 --dirty   -> data/reviews_dirty.csv (some bad rows)

Sizes can be written as 100, 50, 10k, 100k or 1m.
The same size and seed always give exactly the same file.
"""

import argparse
import csv
import random
from pathlib import Path

PRODUCTS = ["phone", "charger", "headphones", "laptop bag", "kettle", "rice cooker",
            "desk lamp", "water bottle", "keyboard", "air fryer", "backpack", "power bank"]

GOOD = ["Great {p}, fast delivery", "Love this {p}!", "Excellent {p}, works perfectly",
        "Really happy with the {p}", "Best {p} I have bought", "Good value {p}, would buy again",
        "The {p} arrived early and works well", "Amazing quality for the price"]
OKAY = ["Okay for the price", "The {p} is fine, nothing special", "Average {p}, does the job",
        "Not bad, but the {p} feels cheap", "Delivery was slow but the {p} is okay"]
BAD = ["Battery died in a week", "The {p} broke after two days", "Terrible {p}, do not buy",
       "Very disappointed with this {p}", "Arrived damaged and late", "Poor quality {p}, asked for a refund",
       "The {p} stopped working, waste of money"]


def parse_size(text: str) -> int:
    text = text.lower().replace(",", "").replace("_", "")
    if text.endswith("k"):
        return int(float(text[:-1]) * 1_000)
    if text.endswith("m"):
        return int(float(text[:-1]) * 1_000_000)
    return int(text)


def make_text(rng: random.Random, rating: int) -> str:
    pool = GOOD if rating >= 4 else OKAY if rating == 3 else BAD
    text = rng.choice(pool).format(p=rng.choice(PRODUCTS))
    roll = rng.random()          # some messiness for the Chapter 3 cleaning steps
    if roll < 0.05:
        text = text.upper()
    elif roll < 0.10:
        text = "  " + text.replace(" ", "   ", 1) + "  "
    elif roll < 0.13:
        text = text.replace(", ", "<br>", 1) if ", " in text else "<b>" + text + "</b>"
    return text


def bad_row(rng: random.Random, n: int) -> list[str]:
    """A faulty row for the Chapter 4 error-handling work."""
    kind = n % 6
    text = make_text(rng, 3)
    if kind == 0:
        return [text, "five"]          # rating is not a number
    if kind == 1:
        return [text, ""]              # rating missing
    if kind == 2:
        return [text, "7"]             # rating out of range
    if kind == 3:
        return ["", "4"]               # empty review
    if kind == 4:
        return [text, "0"]             # rating out of range
    return [text]                      # a column missing


def main() -> None:
    ap = argparse.ArgumentParser(description="Make practice review files.")
    ap.add_argument("size", help="number of reviews, e.g. 100, 10k, 1m")
    ap.add_argument("--dirty", action="store_true", help="mix in about 2%% faulty rows")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", help="output file (default: data/reviews_<size>.csv)")
    args = ap.parse_args()

    n = parse_size(args.size)
    name = "reviews_dirty.csv" if args.dirty else f"reviews_{args.size.lower()}.csv"
    out = Path(args.out) if args.out else Path("data") / name
    out.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    bad = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "rating"])
        for i in range(n):
            if args.dirty and rng.random() < 0.02:
                w.writerow(bad_row(rng, bad))
                bad += 1
                continue
            rating = rng.choices([1, 2, 3, 4, 5], weights=[12, 8, 15, 30, 35])[0]
            w.writerow([make_text(rng, rating), rating])

    extra = f", {bad} of them faulty" if args.dirty else ""
    print(f"Wrote {n:,} reviews to {out}{extra}")


if __name__ == "__main__":
    main()
