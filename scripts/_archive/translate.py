#!/usr/bin/env python3
"""
translate.py — Generate a draft translation from a source text using Claude.

Usage:
    python scripts/translate.py <text-id> <source-file>

Example:
    python scripts/translate.py hippolytus-refutation-6 translations/queue/hippolytus-refutation-6.txt
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DRAFTS_DIR = PROJECT_ROOT / "translations" / "drafts"


def load_glossary():
    with open(DATA_DIR / "glossary.json") as f:
        data = json.load(f)
    return data["terms"]


def load_texts():
    with open(DATA_DIR / "texts.json") as f:
        return json.load(f)


def save_texts(data):
    with open(DATA_DIR / "texts.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_text(texts_data, text_id):
    for text in texts_data["texts"]:
        if text["id"] == text_id:
            return text
    return None


def format_glossary_instructions(terms):
    lines = []
    for term in terms:
        entry = f"- {term['original']} ({term['transliteration']}): "
        if term.get("preserve_untranslated"):
            entry += f"preserve as '{term['transliteration']}' in relevant contexts; "
        entry += f"render as '{term['rendering']}'"
        if term.get("alt_renderings"):
            entry += f" (alternatives: {', '.join(term['alt_renderings'])})"
        entry += f". {term['usage_note']}"
        lines.append(entry)
    return "\n".join(lines)


def build_system_prompt(glossary_terms):
    glossary_block = format_glossary_instructions(glossary_terms)

    return f"""You are assisting a classicist in translating early Christian texts from Greek and Latin into English. The translator has a Classics degree and is proficient in Latin. Your role is to produce an accurate, readable draft translation that the translator will then review, correct, and annotate.

Translation principles:
- Translate into clear, readable modern English while preserving theological precision
- Do NOT flatten technical theological terms into generic English. These terms carry specific weight and their translation choices matter.
- For the following key terms, use the specified English rendering but include the original Greek/Latin in parentheses on first use:

{glossary_block}

- Preserve the section, chapter, and paragraph structure of the original exactly
- Where a passage is genuinely ambiguous, flag it explicitly with [AMBIGUOUS: explanation of the issue and possible readings]
- Where variant readings exist between manuscripts, note them with [VARIANT: description]
- When the text quotes or alludes to Scripture, identify the reference with [SCRIPTURE: Book Chapter:Verse]
- When the text references or quotes other Church Fathers or known Gnostic texts, identify them with [REFERENCE: source]
- Where the Greek is unclear or corrupt, provide the Latin rendering from the Patrologia Graeca facing column if available, flagged as [LATIN: Latin text] for the translator's cross-reference
- Do not add interpretive commentary in the translation itself — save observations for the notes section

Output format — respond with a JSON object containing:
{{
  "introduction": "Draft contextual introduction (2-4 paragraphs). Who wrote this, when, why. What theological questions does it address. How does it relate to debates about the nature of divinity, inner knowledge, and theosis. The translator will edit this.",
  "translation": [
    {{
      "section": "section/chapter number from original",
      "original_ref": "PG column or line reference",
      "text": "The English translation of this section"
    }}
  ],
  "translator_notes": [
    {{
      "ref": "section reference",
      "note": "Observation about translation choice, theological term, ambiguity, or significance that the translator should consider for their annotations"
    }}
  ],
  "flagged_passages": [
    {{
      "ref": "section reference",
      "issue": "Description of the problem (ambiguity, corrupt text, disputed reading, etc.)",
      "suggestion": "Suggested resolution or options for the translator to consider"
    }}
  ]
}}"""


def translate(text_id, source_file):
    texts_data = load_texts()
    text_meta = find_text(texts_data, text_id)

    if not text_meta:
        print(f"Error: text ID '{text_id}' not found in texts.json")
        sys.exit(1)

    source_path = Path(source_file)
    if not source_path.exists():
        print(f"Error: source file '{source_file}' not found")
        sys.exit(1)

    source_text = source_path.read_text(encoding="utf-8")
    glossary_terms = load_glossary()
    system_prompt = build_system_prompt(glossary_terms)

    user_prompt = f"""Please translate the following {text_meta['language']} text into English.

Text: {text_meta['title']}
Author: {text_meta['author']} ({text_meta['author_dates']})
Source: {text_meta['source']}
Critical edition: {text_meta['critical_edition']}

Context: {text_meta['description']}

--- BEGIN SOURCE TEXT ---
{source_text}
--- END SOURCE TEXT ---

Produce the translation as the specified JSON object."""

    client = anthropic.Anthropic()

    print(f"Sending {text_meta['title']} to Claude for translation...")
    print(f"Source text length: {len(source_text)} characters")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    response_text = message.content[0].text

    # Try to parse the JSON from the response
    try:
        # Handle case where response might be wrapped in markdown code block
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        draft = json.loads(cleaned)
    except json.JSONDecodeError:
        print("Warning: Could not parse response as JSON. Saving raw response.")
        draft = {"raw_response": response_text}

    # Save draft
    output = {
        "text_id": text_id,
        "metadata": text_meta,
        "draft": draft,
        "model": "claude-sonnet-4-20250514",
        "date_drafted": str(date.today()),
        "usage": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        },
    }

    output_path = DRAFTS_DIR / f"{text_id}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Draft saved to {output_path}")

    # Update status in texts.json
    text_meta["status"] = "drafted"
    text_meta["date_drafted"] = str(date.today())
    save_texts(texts_data)
    print(f"Status updated to 'drafted' in texts.json")

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a draft translation using Claude")
    parser.add_argument("text_id", help="Text ID from texts.json")
    parser.add_argument("source_file", help="Path to the source text file (Greek/Latin)")
    args = parser.parse_args()

    translate(args.text_id, args.source_file)
