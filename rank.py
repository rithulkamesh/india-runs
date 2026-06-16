"""Entry point — run ranker from command line."""

import argparse
import csv
import sys
import time

sys.path.insert(0, ".")

from src.ranker.pipeline import run_pipeline_streaming


def write_submission(results: list[dict], output_path: str):
    """Write results to submission CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in results:
            writer.writerow([
                r["candidate_id"],
                r["rank"],
                r["score"],
                r["reasoning"],
            ])
    print(f"Wrote {len(results)} candidates to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="India Runs Candidate Ranker")
    parser.add_argument(
        "--candidates", "-c",
        required=True,
        help="Path to candidates.jsonl file",
    )
    parser.add_argument(
        "--out", "-o",
        default="submission.csv",
        help="Output CSV path (default: submission.csv)",
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=100,
        help="Number of top candidates to return (default: 100)",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of candidates to process (for testing)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("INDIA RUNS — Intelligent Candidate Discovery & Ranking")
    print("=" * 60)

    t_start = time.time()

    results = run_pipeline_streaming(args.candidates, top_k=args.top_k, limit=args.limit)

    write_submission(results, args.out)

    elapsed = time.time() - t_start
    print(f"\nTotal time: {elapsed:.2f}s")
    print(f"Top candidates ranked: {len(results)}")
    print(f"\nTop 5:")
    for r in results[:5]:
        print(f"  #{r['rank']} {r['candidate_id']} score={r['score']:.4f}")
        print(f"       {r['reasoning'][:120]}...")


if __name__ == "__main__":
    main()
