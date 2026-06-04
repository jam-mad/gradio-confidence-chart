import gradio as gr
from gradio_confidencechart import ConfidenceChart
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    top_k=None,
)


def analyze(text: str) -> dict:
    if not text or not text.strip():
        return {}
    results = classifier(text)
    scores = results[0] if isinstance(results[0], list) else results
    return {item["label"]: item["score"] for item in scores}


with gr.Blocks(title="Confidence Chart Demo") as demo:
    gr.Markdown(
        """
        # Confidence Chart
        A custom Gradio component that renders animated confidence bar charts
        for ML classification results.

        Try typing a sentence below — results update live.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            text_input = gr.Textbox(
                label="Input text",
                placeholder="Type something like 'I love this movie!' or 'This was terrible.'",
                lines=3,
            )
            submit_btn = gr.Button("Analyze", variant="primary")
            gr.Examples(
                examples=[
                    ["I absolutely love this, it's fantastic!"],
                    ["This is the worst experience I've ever had."],
                    ["It was okay, nothing special really."],
                    ["Unbelievably good. I can't recommend it enough."],
                    ["Disappointing and frustrating from start to finish."],
                ],
                inputs=text_input,
            )

        with gr.Column(scale=1):
            chart = ConfidenceChart(
                label="Sentiment Analysis",
                show_label=True,
            )

    text_input.change(
        fn=analyze,
        inputs=text_input,
        outputs=chart,
        show_progress="hidden",
    )
    submit_btn.click(
        fn=analyze,
        inputs=text_input,
        outputs=chart,
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())