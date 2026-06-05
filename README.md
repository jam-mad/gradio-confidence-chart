# gradio-confidence-chart

A custom [Gradio](https://gradio.app) component that renders animated confidence bar charts for ML classification results, plus two demo apps built on top of it.

## What's in here

```
confidencechart/          # the component itself (pip-installable)
  backend/                # Python class
  frontend/               # Svelte 5 component
  demo/
    app.py                # live sentiment analysis demo
    app_fool_the_model.py # adversarial challenge game
  scripts/
    find_foolers.py       # ETL script used to find the challenge sentences
```

## Quick start

```bash
cd confidencechart
pip install -e ".[dev]"
gradio cc dev
```

See [`confidencechart/README.md`](confidencechart/README.md) for full documentation.
