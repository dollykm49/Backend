import os
import base64
import json
from pathlib import Path

from openai import OpenAI

from app.services.algorithms import normalize_scores, compute_confidence

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _encode(path: Path) -> str:
    b = path.read_bytes()
    return f"data:image/jpeg;base64,{base64.b64encode(b).decode()}"


def _call_ai_grader(front_path: Path, back_path: Path, style: str) -> dict:
    """
    One AI 'opinion' pass.
    style = 'strict' or 'lenient' (slightly different wording to get variety).
    """

    style_text = "Be slightly strict in scoring." if style == "strict" else "Be slightly lenient but honest."

    system_prompt = f"""
You are a professional comic book grader with deep experience (CGC-style).
Analyze the FRONT and BACK cover images for:

- Spine ticks, color-breaking and non-color-breaking
- Creases, bends, folds
- Corner blunting or rounding
- Surface gloss, scuffs, scratches, stains
- Color vibrancy, fading, discoloration
- Centering and print alignment
- Any signs of restoration (color touch, glue, trimming, pressing artifacts)

{style_text}

Return ONLY JSON. No extra commentary.
Use this exact JSON structure:

{{
  "corners": number,
  "spine": number,
  "surface": number,
  "centering": number,
  "color": number,
  "restoration_suspected": boolean,
  "pressing_benefit": "none" | "low" | "medium" | "high",
  "page_color": "white" | "off-white" | "cream" | "tan" | "brittle",
  "notes": "short description of key defects and overall condition"
}}
"""

    user_content = [
        {
            "type": "input_text",
            "text": "Grade this comic from 0.5–10.0 subgrades. First image is the FRONT, second is the BACK.",
        },
        {
            "type": "input_image",
            "image_url": {"url": _encode(front_path)},
        },
        {
            "type": "input_image",
            "image_url": {"url": _encode(back_path)},
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception:
        raise ValueError("AI returned invalid JSON")

    return data


def grade_comic(front_path: Path, back_path: Path) -> dict:
    """
    Hybrid grading:
    - Two AI passes (strict + lenient)
    - Scores normalized by algorithm
    - Confidence computed from disagreement
    """

    # Two slightly different 'opinions'
    opinion_strict = _call_ai_grader(front_path, back_path, style="strict")
    opinion_lenient = _call_ai_grader(front_path, back_path, style="lenient")

    # Average raw scores for subgrades
    raw_scores = {}
    for key in ["corners", "spine", "surface", "centering", "color"]:
        a = float(opinion_strict.get(key, 0))
        b = float(opinion_lenient.get(key, 0))
        raw_scores[key] = (a + b) / 2.0

    # Pass through our normalization algorithm
    normalized = normalize_scores(raw_scores)

    # Confidence based on how far apart the two opinions were
    confidence = compute_confidence(opinion_strict, opinion_lenient)

    # Merge notes + flags
    notes = opinion_strict.get("notes", "") or opinion_lenient.get("notes", "")
    flags = {
        "restoration_suspected": bool(
            opinion_strict.get("restoration_suspected") or opinion_lenient.get("restoration_suspected")
        ),
        "pressing_benefit": opinion_strict.get("pressing_benefit") or opinion_lenient.get("pressing_benefit"),
        "page_color": opinion_strict.get("page_color") or opinion_lenient.get("page_color"),
    }

    return {
        "subgrades": normalized,
        "final": normalized["final"],
        "notes": notes,
        "confidence": confidence,
        "flags": flags,
    }
