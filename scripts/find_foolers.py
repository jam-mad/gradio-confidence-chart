"""
find_foolers.py

Pulls sentences from the SST-2 dataset (the same data this model was trained on),
runs each through the sentiment classifier, and flags cases where the model's
prediction disagrees with the human label.

Those disagreements are the honest definition of "fooling the model":
a human labeled it one way, the model says the other.

Output: foolers.json sorted by how confident (and wrong) the model was.

Usage:
    pip install datasets
    python find_foolers.py
"""

import json
from transformers import pipeline
from datasets import load_dataset


MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
MIN_CONFIDENCE = 0.90
OUTPUT_FILE = "foolers.json"
DATASET_NAME = "stanfordnlp/sst2"


def human_label(row_label: int) -> str:
    return "POSITIVE" if row_label == 1 else "NEGATIVE"


def main() -> None:
    print("Loading model...")
    clf = pipeline("text-classification", model=MODEL, top_k=None)

    print("Loading SST-2 dataset...")
    ds = load_dataset(DATASET_NAME, split="validation")

    sentences = [row["sentence"] for row in ds]
    human_labels = [human_label(row["label"]) for row in ds]

    print(f"Running classifier on {len(sentences)} sentences...")
    batch_size = 64
    all_results = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i : i + batch_size]
        all_results.extend(clf(batch))
        if i % 256 == 0:
            print(f"  {i}/{len(sentences)}")

    foolers = []
    for sentence, human, result in zip(sentences, human_labels, all_results):
        scores = {r["label"]: r["score"] for r in result}
        model_label = max(scores, key=scores.get)
        model_confidence = scores[model_label]

        if model_label != human and model_confidence >= MIN_CONFIDENCE:
            foolers.append(
                {
                    "sentence": sentence,
                    "human_label": human,
                    "model_confidence": round(model_confidence, 4),
                    "positive_score": round(scores.get("POSITIVE", 0), 4),
                    "negative_score": round(scores.get("NEGATIVE", 0), 4),
                    "fool_type": f"human={human}, model={model_label}",
                }
            )

    foolers.sort(key=lambda x: x["model_confidence"], reverse=True)

    with open(OUTPUT_FILE, "w") as fp:
        json.dump(foolers, fp, indent=2)

    print(f"\nFound {len(foolers)} foolers out of {len(sentences)} sentences.")
    print(f"Saved to {OUTPUT_FILE}\n")

    print("Top 10 most confident wrong answers:")
    print("-" * 72)
    for entry in foolers[:10]:
        print(f"  [{entry['fool_type']}] conf={entry['model_confidence']:.3f}")
        print(f"  {entry['sentence']}")
        print()


if __name__ == "__main__":
    main()