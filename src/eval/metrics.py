"""Evaluation metrics — NDCG@K, MRR, MAP, P@K, Recall@K."""

import math
from typing import Optional


def dcg_at_k(relevance: list[float], k: int) -> float:
    """Compute DCG@K."""
    relevance = relevance[:k]
    if not relevance:
        return 0.0
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevance))


def ndcg_at_k(relevance: list[float], k: int) -> float:
    """Compute NDCG@K."""
    dcg = dcg_at_k(relevance, k)
    ideal = dcg_at_k(sorted(relevance, reverse=True), k)
    return dcg / ideal if ideal > 0 else 0.0


def mrr(ranked_relevant: list[bool]) -> float:
    """Compute Mean Reciprocal Rank."""
    for i, rel in enumerate(ranked_relevant, start=1):
        if rel:
            return 1.0 / i
    return 0.0


def average_precision(ranked_relevant: list[bool]) -> float:
    """Compute Average Precision."""
    num_relevant = sum(ranked_relevant)
    if num_relevant == 0:
        return 0.0

    precisions = []
    relevant_so_far = 0
    for i, rel in enumerate(ranked_relevant, start=1):
        if rel:
            relevant_so_far += 1
            precisions.append(relevant_so_far / i)

    return sum(precisions) / num_relevant if precisions else 0.0


def precision_at_k(ranked_relevant: list[bool], k: int) -> float:
    """Compute Precision@K."""
    return sum(ranked_relevant[:k]) / k if k > 0 else 0.0


def recall_at_k(ranked_relevant: list[bool], k: int, total_relevant: int) -> float:
    """Compute Recall@K."""
    if total_relevant == 0:
        return 0.0
    return sum(ranked_relevant[:k]) / total_relevant


def evaluate_ranking(
    ranked_ids: list[str],
    ground_truth: dict[str, float],
) -> dict:
    """Evaluate a ranking against ground truth relevance scores.

    Args:
        ranked_ids: List of candidate_ids in ranked order
        ground_truth: Dict mapping candidate_id -> relevance score

    Returns:
        Dict with NDCG@10, NDCG@50, MAP, P@10, MRR
    """
    relevance = [ground_truth.get(cid, 0.0) for cid in ranked_ids]
    binary_relevant = [r > 0.5 for r in relevance]
    total_relevant = sum(1 for v in ground_truth.values() if v > 0.5)

    return {
        "ndcg@10": ndcg_at_k(relevance, 10),
        "ndcg@50": ndcg_at_k(relevance, 50),
        "map": average_precision(binary_relevant),
        "p@10": precision_at_k(binary_relevant, 10),
        "p@5": precision_at_k(binary_relevant, 5),
        "mrr": mrr(binary_relevant),
        "recall@100": recall_at_k(binary_relevant, 100, total_relevant),
    }


def compute_composite(metrics: dict) -> float:
    """Compute the competition composite score.

    Final composite = 0.50 * NDCG@10 + 0.30 * NDCG@50 + 0.15 * MAP + 0.05 * P@10
    """
    return (
        0.50 * metrics["ndcg@10"]
        + 0.30 * metrics["ndcg@50"]
        + 0.15 * metrics["map"]
        + 0.05 * metrics["p@10"]
    )


def print_evaluation_report(metrics: dict):
    """Print a formatted evaluation report."""
    composite = compute_composite(metrics)
    print("=" * 50)
    print("EVALUATION REPORT")
    print("=" * 50)
    for k, v in metrics.items():
        print(f"  {k:>12}: {v:.4f}")
    print(f"  {'composite':>12}: {composite:.4f}")
    print("=" * 50)
