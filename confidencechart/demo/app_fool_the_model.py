import gradio as gr
from gradio_confidencechart import ConfidenceChart
from transformers import pipeline

HINT = "💡"
EXAMPLE = "📝"
SUCCESS = "🏆"
MISLEAD = "😈"
CONFUSED = "🤔"
SUSPICIOUS = "😒"
FAIL = "❌"

classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    top_k=None,
)

# Each challenge uses a real sentence from the SST-2 validation set. This is the same
# dataset this model was trained on. A human critic labeled each sentence one way;
# the model confidently says the opposite. The player's job is to write something
# that exploits the same weakness.
CHALLENGES = [
    {
        "target": "POSITIVE",
        "instruction": "### Challenge 1: The backhanded compliment\nThe model should say **NEGATIVE**. Get it to say **POSITIVE**.\n\nThis critic gave the film a bad review. The model rated it positive anyway at 99.96% confidence. Why? Because 'enjoy' drowns out everything else.",
        "hint": f"{HINT} The model latches onto words like 'enjoy', 'fun', 'love', 'great' even when they're buried in qualifiers. Try writing a lukewarm or conditional compliment. The more you bury the praise, the more the model ignores the burying.",
        "example": f"{EXAMPLE} Real review that fooled it (human=NEGATIVE, model=POSITIVE, 99.96%):\n*\"the lower your expectations, the more you'll enjoy it.\"*",
    },
    {
        "target": "NEGATIVE",
        "instruction": "### Challenge 2: Glorious failure\nThe model should say **POSITIVE**. Get it to say **NEGATIVE**.\n\nA critic called this film a 'glorious failure' (a compliment within the context of the rest of the review). The model saw 'failure' and rated it negative at 99.94%.",
        "hint": f"{HINT} The model is bad at understanding that negative words can be used positively. Try writing genuine praise using words like 'failure', 'disaster', 'terrible', 'ugly', 'dark'. Frame the negative as what makes it good.",
        "example": f"{EXAMPLE} Real review that fooled it (human=POSITIVE, model=NEGATIVE, 99.94%):\n*\"if steven soderbergh's solaris is a failure it is a glorious failure.\"*",
    },
    {
        "target": "POSITIVE",
        "instruction": "### Challenge 3: Negation blindness\nThe model should say **NEGATIVE**. Get it to say **POSITIVE**.\n\nOne of the most devastating reviews in the dataset. The model called it positive at 99.87%. It completely missed the negation.",
        "hint": f"{HINT} The model struggles with 'don't', 'won't', 'can't', 'not'. Try writing something clearly negative using a negated positive: 'everything you don't want', 'nothing you'd hope for', 'not a single good moment'. Watch the model get confused.",
        "example": f"{EXAMPLE} Real review that fooled it (human=NEGATIVE, model=POSITIVE, 99.87%):\n*\"it's everything you don't go to the movies for.\"*",
    },
    {
        "target": "NEGATIVE",
        "instruction": "### Challenge 4: The mixed review\nThe model should say **POSITIVE**. Get it to say **NEGATIVE**.\n\nA warm, overall positive review. The critic liked this film. The model rated it negative at 99.38% because the second half of the sentence overwhelmed the first.",
        "hint": f"{HINT} The model weighs the end of a sentence more heavily than the beginning. Try starting with genuine praise then ending with a mild criticism. 'Great performances, shame about the script' type constructions tend to flip the model negative even when the overall sentiment is positive.",
        "example": f"{EXAMPLE} Real review that fooled it (human=POSITIVE, model=NEGATIVE, 99.38%):\n*\"harrison's flowers puts its heart in the right place, but its brains are in no particular place at all.\"*",
    },
]


def get_challenge(index: int) -> tuple:
    c = CHALLENGES[index % len(CHALLENGES)]
    return c["instruction"], c["hint"], c["example"], c["target"]


def score_attempt(text: str, target: str) -> tuple:
    if not text or not text.strip():
        return {}, "Start typing to see your score...", 0

    results = classifier(text)
    scores = results[0] if isinstance(results[0], list) else results
    confidences = {item["label"]: item["score"] for item in scores}

    target_score = confidences.get(target, 0)
    opposite = "NEGATIVE" if target == "POSITIVE" else "POSITIVE"
    opposite_score = confidences.get(opposite, 0)
    fool_score = round(target_score * 100)

    if fool_score >= 90:
        verdict = (
            f"{SUCCESS} **Perfect fool!** The model is {target_score*100:.1f}% sure it's {target}. "
            f"You exploited the same blind spot the real critic did."
        )
    elif fool_score >= 70:
        verdict = (
            f"{MISLEAD} **Nice!** The model leans {target_score*100:.1f}% toward {target}. "
            f"Partially fooled. Push the {target.lower()} signal harder."
        )
    elif fool_score >= 50:
        verdict = (
            f"{CONFUSED} **The model is confused** ({target_score*100:.1f}% {target} vs {opposite_score*100:.1f}% {opposite}). "
            f"Close. Try leaning harder into the {target.lower()} language."
        )
    elif fool_score >= 30:
        verdict = (
            f"{SUSPICIOUS} **Getting suspicious** ({opposite_score*100:.1f}% {opposite}). "
            f"Your {opposite.lower()} words are louder than your {target.lower()} ones. Try a different angle."
        )
    else:
        verdict = (
            f"{FAIL} **Busted!** The model is {opposite_score*100:.1f}% sure it's {opposite}. "
            f"It's pattern-matching on words from training data, not reading your intent. "
            f"What if you avoided obvious {opposite.lower()} words altogether?"
        )

    return confidences, verdict, fool_score


def next_challenge(current_index: int) -> tuple:
    new_index = (current_index + 1) % len(CHALLENGES)
    instruction, hint, example, target = get_challenge(new_index)
    return new_index, instruction, hint, example, target, {}, "Start typing to see your score...", ""


with gr.Blocks(title="Fool the Sentiment Model") as demo:
    challenge_index = gr.State(0)
    target_label = gr.State(CHALLENGES[0]["target"])

    gr.Markdown(
        """
        # Fool the Sentiment Model

        A sentiment classifier was trained on thousands of real movie reviews.
        These are real sentences from that dataset where the model gets it wrong.

        Each challenge shows you a sentence that fooled the model and asks you to
        write something that exploits the same weakness.

        The chart updates live as you type. **Fool Score** = how much the model
        believes the target label. 100 is a perfect fool.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            challenge_box = gr.Markdown(value=CHALLENGES[0]["instruction"])
            hint_box = gr.Markdown(value=CHALLENGES[0]["hint"])
            example_box = gr.Markdown(value=CHALLENGES[0]["example"])

            attempt_input = gr.Textbox(
                label="Your attempt",
                placeholder="Type your sentence here...",
                lines=4,
            )

            with gr.Row():
                next_btn = gr.Button("Next Challenge", variant="secondary")
                fool_score_display = gr.Number(
                    label="Fool Score (0-100)",
                    value=0,
                    interactive=False,
                )

            verdict = gr.Markdown(value="Start typing to see your score...")

        with gr.Column(scale=1):
            chart = ConfidenceChart(
                label="What the model thinks",
                show_label=True,
            )

    attempt_input.change(
        fn=score_attempt,
        inputs=[attempt_input, target_label],
        outputs=[chart, verdict, fool_score_display],
        show_progress="hidden",
    )

    next_btn.click(
        fn=next_challenge,
        inputs=[challenge_index],
        outputs=[
            challenge_index,
            challenge_box,
            hint_box,
            example_box,
            target_label,
            chart,
            verdict,
            attempt_input,
        ],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())