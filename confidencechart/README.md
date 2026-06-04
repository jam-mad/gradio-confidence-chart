---
tags: [gradio-custom-component, gradio-template-Label, gradio, classification, visualization, chart]
title: gradio_confidencechart
short_description: A custom Gradio component that renders animated, interactive confidence bar charts for ML classification results
colorFrom: violet
colorTo: sky
sdk: gradio
sdk_version: 6.16.0
pinned: false
app_file: demo/app.py
license: apache-2.0
---

# `gradio_confidencechart`

A custom [Gradio](https://gradio.app) component that swaps out the default `gr.Label` for animated, color-coded confidence bar charts.

[![GitHub](https://img.shields.io/badge/github-jam--mad%2Fgradio--confidence--chart-blue)](https://github.com/jam-mad/gradio-confidence-chart)

## Installation

```bash
pip install gradio_confidencechart
```

## Usage

```python
import gradio as gr
from gradio_confidencechart import ConfidenceChart

def classify(text: str) -> dict:
    return {"POSITIVE": 0.97, "NEGATIVE": 0.03}

with gr.Blocks() as demo:
    text = gr.Textbox()
    chart = ConfidenceChart(label="Results")
    text.change(fn=classify, inputs=text, outputs=chart)

demo.launch()
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `value` | `dict[str, float] \| str \| float \| None` | `None` | Classification results as a label-to-confidence dict |
| `num_top_classes` | `int \| None` | `None` | Max number of classes to display |
| `label` | `str \| None` | `None` | Component label shown above the chart |
| `show_label` | `bool \| None` | `None` | Whether to show the label |
| `color` | `str \| None` | `None` | Optional background color |
| `show_heading` | `bool` | `True` | Whether to show the top prediction badge |

## How it works

Drop-in replacement for `gr.Label`. Pass it a `dict[str, float]` of class names to confidence scores and it renders animated horizontal bars using Svelte's `tweened` motion store with `cubicOut` easing.

Built on Gradio's custom component system: a Python class sorts and validates data via `postprocess()`, a Svelte 5 component handles rendering, both share the same `LabelData` schema.

## Demos

### Sentiment Analysis (`demo/app.py`)

Live sentiment scoring with `distilbert-base-uncased-finetuned-sst-2-english`. Bars update as you type.

### Fool the Model (`demo/app_fool_the_model.py`)

An adversarial challenge game. Each round shows a real sentence from the SST-2 validation set where a human critic and the model disagree. Your job is to write something that exploits the same weakness.

Challenge sentences came from `scripts/find_foolers.py`, which runs all 872 SST-2 validation sentences through the classifier and flags high-confidence wrong answers (above 90%). The most surprising ones were picked by hand.

Three patterns show up a lot:

- **Negation blindness** -- "it's everything you don't go to the movies for" scores 99.87% POSITIVE. The model sees "go to the movies" and ignores the "don't".
- **Keyword fixation** -- "failure" triggers NEGATIVE even in "a glorious failure", which is clearly a compliment.
- **Recency bias** -- the last clause tends to win. Praise up front, one mild dig at the end, and the model often calls it negative.

More on these failure modes: [toptal.com/deep-learning/4-sentiment-analysis-accuracy-traps](https://www.toptal.com/deep-learning/4-sentiment-analysis-accuracy-traps) and the [CheckList paper](https://arxiv.org/abs/2005.04118) (Ribeiro et al., 2020).

## Development

```bash
git clone https://github.com/jam-mad/gradio-confidence-chart
cd gradio-confidence-chart
python -m venv .venv && source .venv/bin/activate
pip install -e "confidencechart[dev]"
cd confidencechart && gradio cc dev
```