# Theosis Library

Scholarly translations of early Christian texts that have never been translated into English, with a focus on patristic writings about Gnostic Christianity, the concept of theosis (divinization), and the question of whether divinity is the exclusive property of Christ or an inner spark present in all beings.

**Website:** [theosislibrary.com](https://theosislibrary.com)
**Publisher:** Hyperborean Press

## What This Is

The *Patrologia Graeca* contains 161 volumes of Greek Christian writing spanning 1,400 years. Only a fraction has been translated into English. The Latin Fathers contain equally rich material. Theosis Library is working through these texts systematically, producing modern English translations with scholarly annotations.

Translations are AI-assisted (Claude by Anthropic generates initial drafts from the original Greek and Latin), then reviewed and corrected by the translator against the original text, with scholarly annotations added. Every published translation links to the original source text.

## Project Structure

```
site/                    Static website (HTML/CSS/JS)
translations/
  queue/                 Source texts queued for translation
  drafts/                AI-generated first drafts
  reviewed/              Reviewed and annotated by translator
  published/             Final published versions
scripts/
  translate.py           Generate draft translation via Anthropic API
  publish.py             Convert reviewed translation to HTML
  build_index.py         Rebuild library index and search
data/
  texts.json             Text catalog with status tracking
  glossary.json          Theological term glossary
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Anthropic API key to .env
```

## Translation Pipeline

1. Place source text (Greek/Latin) in `translations/queue/`
2. Generate draft: `python scripts/translate.py <text-id> translations/queue/<file>`
3. Review draft in `translations/drafts/`, correct and annotate, save to `translations/reviewed/`
4. Publish: `python scripts/publish.py <text-id>`

## Deployment

The `site/` directory deploys to Cloudflare Pages via GitHub. Push to `main` to deploy.

## License

Translations: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
Code: MIT
