import argparse
import json
import os
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from tabulate import tabulate
from runner import run

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "user_config")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")


def main():
    parser = argparse.ArgumentParser(description="CASI — AI Secret Leakage Evaluator")
    parser.add_argument(
        "--config", default=os.path.join(CONFIG_DIR, "run_config.yaml"),
        help="Path to run config YAML file",
    )
    parser.add_argument(
        "--scenarios", default=os.path.join(CONFIG_DIR, "scenarios.yaml"),
        help="Path to scenarios YAML file",
    )
    parser.add_argument(
        "--models", default=os.path.join(CONFIG_DIR, "models.yaml"),
        help="Path to models YAML file",
    )
    args = parser.parse_args()

    load_dotenv(os.path.join(CONFIG_DIR, ".env"))

    print("\nRunning CASI evaluation...\n")
    results = run(args.scenarios, args.models, args.config)

    # Full responses first
    print("=" * 60)
    print("FULL RESPONSES")
    print("=" * 60)
    for r in results:
        print(f"\n--- {r['model']} / {r['scenario']} / run {r['run']} ---")
        for rule in r["rules"]:
            status = "MATCHED" if rule["matched"] else "passed"
            print(f"  [{status}] {rule['rule']}")
        print()
        print(r["response"])
        print()

    # Per-run detail table
    detail_rows = []
    for r in results:
        resp = r["response"] or ""
        snippet = resp[:80] + ("..." if len(resp) > 80 else "")
        triggered = ", ".join(
            rule["rule"] for rule in r["rules"] if rule["matched"]
        ) or "-"
        detail_rows.append([
            r["model"], r["scenario"], r["run"],
            "YES" if r["leaked"] else "NO",
            triggered, snippet,
        ])

    print(tabulate(
        detail_rows,
        headers=["Model", "Scenario", "Run", "Leaked?", "Triggered Rules", "Response Snippet"],
        tablefmt="grid",
    ))

    # Aggregate summary table
    # Collect all unique rule names across results
    all_rule_names = []
    for r in results:
        for rule in r["rules"]:
            if rule["rule"] not in all_rule_names:
                all_rule_names.append(rule["rule"])

    agg = defaultdict(lambda: {"total": 0, "leaked": 0, "by_rule": defaultdict(int)})
    for r in results:
        key = (r["model"], r["scenario"])
        agg[key]["total"] += 1
        if r["leaked"]:
            agg[key]["leaked"] += 1
        for rule in r["rules"]:
            if rule["matched"]:
                agg[key]["by_rule"][rule["rule"]] += 1

    print()
    summary_rows = []
    for (model, scenario), counts in agg.items():
        rate = counts["leaked"] / counts["total"]
        row = [
            model, scenario,
            f"{counts['leaked']}/{counts['total']}",
            f"{rate:.0%}",
        ]
        for rule_name in all_rule_names:
            row.append(counts["by_rule"].get(rule_name, 0))
        summary_rows.append(row)

    print(tabulate(
        summary_rows,
        headers=["Model", "Scenario", "Leaked", "Leak Rate"] + all_rule_names,
        tablefmt="grid",
    ))

    total_leaked = sum(1 for r in results if r["leaked"])
    print(f"\nOverall: {total_leaked}/{len(results)} tests leaked the secret.\n")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outpath = os.path.join(RESULTS_DIR, f"run_{timestamp}.json")

    summary = {}
    for (model, scenario), counts in agg.items():
        summary[f"{model}/{scenario}"] = {
            "leaked": counts["leaked"],
            "total": counts["total"],
            "leak_rate": counts["leaked"] / counts["total"],
            "by_rule": dict(counts["by_rule"]),
        }

    output = {
        "timestamp": timestamp,
        "overall": {"leaked": total_leaked, "total": len(results)},
        "summary": summary,
        "details": results,
    }
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to {outpath}")


if __name__ == "__main__":
    main()
