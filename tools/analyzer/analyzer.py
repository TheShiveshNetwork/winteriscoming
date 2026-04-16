import argparse
from collections import defaultdict
import pandas as pd
from tabulate import tabulate
import plotext as plt

from common.config import SCRAPED_FILES_PATH, read_json_data


# ✅ Load
def load_files():
    data = read_json_data(SCRAPED_FILES_PATH)
    return data.get("files", [])


# ✅ Flatten into DataFrame
def to_dataframe(files):
    rows = []

    for f in files:
        ctx = f.get("source_context", {})

        rows.append({
            "name": f.get("name"),
            "mimeType": f.get("mimeType"),
            "size": int(f.get("size") or 0),
            "year": ctx.get("year"),
            "subject": ctx.get("subject"),
            "branch": ctx.get("branch"),
            "stream": ctx.get("stream"),
            "cycle": ctx.get("cycle"),
        })

    return pd.DataFrame(rows)


# ✅ Filters
def apply_filters(df, args):
    if args.year:
        df = df[df["year"] == args.year]
    if args.subject:
        df = df[df["subject"] == args.subject]
    if args.branch:
        df = df[df["branch"] == args.branch]
    if args.stream:
        df = df[df["stream"] == args.stream]
    if args.cycle:
        df = df[df["cycle"] == args.cycle]

    return df


# ✅ Default analysis table
def default_analysis(df):
    print("\n=== DATASET SUMMARY ===\n")

    summary = {
        "Total Files": len(df),
        "Total Size (MB)": round(df["size"].sum() / (1024 * 1024), 2),
        "Unique Years": df["year"].nunique(),
        "Unique Branches": df["branch"].nunique(),
    }

    print(tabulate(summary.items(), headers=["Metric", "Value"]))


# ✅ Grouped table
def group_analysis(df, key):
    grouped = df.groupby(key).agg(
        count=("name", "count"),
        total_size_mb=("size", lambda x: round(x.sum() / (1024 * 1024), 2))
    ).sort_values(by="count", ascending=False)

    print(f"\n=== GROUPED BY {key.upper()} ===\n")
    print(tabulate(grouped, headers="keys", tablefmt="pretty"))

    return grouped


# ✅ Terminal bar chart
def plot_bar(grouped, key):
    labels = list(grouped.index.astype(str))
    values = grouped["count"].tolist()

    plt.clear_data()
    plt.bar(labels, values)
    plt.title(f"Distribution by {key}")
    plt.xlabel(key)
    plt.ylabel("Count")
    plt.show()


# ✅ Terminal pie chart (approx using bar)
def plot_pie_like(grouped, key):
    print(f"\n=== PIE (Top Categories) ===\n")

    total = grouped["count"].sum()

    for idx, row in grouped.head(10).iterrows():
        percent = (row["count"] / total) * 100
        bar = "█" * int(percent // 2)
        print(f"{idx}: {bar} {percent:.2f}%")


# ✅ CLI
def main():
    parser = argparse.ArgumentParser(description="Dataset Analyzer")

    # Filters
    parser.add_argument("--year", type=str)
    parser.add_argument("--subject", type=str)
    parser.add_argument("--branch", type=str)
    parser.add_argument("--stream", type=str)
    parser.add_argument("--cycle", type=str)

    # Analysis
    parser.add_argument("--group-by", type=str)
    parser.add_argument("--plot", action="store_true")

    args = parser.parse_args()

    files = load_files()
    df = to_dataframe(files)

    df = apply_filters(df, args)

    # ✅ Default summary
    default_analysis(df)

    # ✅ Group analysis
    if args.group_by:
        grouped = group_analysis(df, args.group_by)

        if args.plot:
            plot_bar(grouped, args.group_by)
            plot_pie_like(grouped, args.group_by)


if __name__ == "__main__":
    main()
