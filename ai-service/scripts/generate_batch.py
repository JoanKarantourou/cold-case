#!/usr/bin/env python3
"""
Batch case generation script.

Generates N mystery cases with varied parameters and stores them in
the database. Can be run manually or on a schedule.

Usage:
    python -m scripts.generate_batch            # generate 5 cases (default)
    python -m scripts.generate_batch --count 10 # generate 10 cases
    python -m scripts.generate_batch --count 3 --era 1970s --difficulty 4
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, Base, engine, ensure_schema
from app.services.case_generator import CaseGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("batch_generator")

# Diverse parameter presets for variety
GENERATION_PRESETS = [
    {"mood_tags": ["dark", "industrial", "cold"], "era": "1980s", "difficulty": 4, "crime_type": "Murder"},
    {"mood_tags": ["nostalgic", "small-town", "warm"], "era": "1960s", "difficulty": 2, "crime_type": "Disappearance"},
    {"mood_tags": ["neon", "urban", "paranoid"], "era": "2010s", "difficulty": 5, "crime_type": "Poisoning"},
    {"mood_tags": ["eerie", "rural", "foggy"], "era": "1950s", "difficulty": 3, "crime_type": "Murder"},
    {"mood_tags": ["coastal", "melancholic", "dark"], "era": "1990s", "difficulty": 3, "crime_type": "Arson / Murder"},
    {"mood_tags": ["sterile", "cold", "urban"], "era": "2000s", "difficulty": 4, "crime_type": "Theft / Murder"},
    {"mood_tags": ["warm", "nostalgic", "rural"], "era": "1970s", "difficulty": 2, "crime_type": "Kidnapping / Suspected Murder"},
    {"mood_tags": ["dark", "eerie", "industrial"], "era": "1980s", "difficulty": 5, "crime_type": "Murder"},
    {"mood_tags": ["foggy", "coastal", "melancholic"], "era": "1960s", "difficulty": 3, "crime_type": "Disappearance"},
    {"mood_tags": ["paranoid", "neon", "sterile"], "era": "2010s", "difficulty": 4, "crime_type": "Poisoning"},
]


async def generate_batch(
    count: int,
    era: str | None = None,
    difficulty: int | None = None,
    crime_type: str | None = None,
) -> list[dict]:
    """Generate a batch of cases and return summaries."""
    ensure_schema()
    Base.metadata.create_all(bind=engine)

    generator = CaseGenerator()
    results = []

    for i in range(count):
        preset = GENERATION_PRESETS[i % len(GENERATION_PRESETS)]
        params = {
            "mood_tags": preset["mood_tags"],
            "era": era or preset["era"],
            "difficulty": difficulty or preset["difficulty"],
            "crime_type": crime_type or preset["crime_type"],
        }

        db = SessionLocal()
        try:
            logger.info(
                f"Generating case {i + 1}/{count} — "
                f"mood={params['mood_tags']}, era={params['era']}, "
                f"difficulty={params['difficulty']}"
            )
            case = await generator.generate_case(db, **params)

            summary = {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "difficulty": case.difficulty,
                "era": case.era,
                "mood_tags": case.mood_tags,
                "suspects": len(case.suspects),
                "evidence": len(case.evidence),
                "files": len(case.case_files),
            }
            results.append(summary)
            logger.info(
                f"  -> {case.case_number} \"{case.title}\" — "
                f"{len(case.suspects)} suspects, {len(case.evidence)} evidence, "
                f"{len(case.case_files)} files"
            )

            # Validate: must have at least 1 guilty suspect
            guilty = [s for s in case.suspects if s.is_guilty]
            if not guilty:
                logger.warning(f"  !! Case {case.case_number} has no guilty suspect — flagging")
            else:
                logger.info(f"  -> Guilty: {guilty[0].name}")

        except Exception as e:
            logger.error(f"  !! Failed to generate case {i + 1}: {e}")
        finally:
            db.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="Batch generate mystery cases")
    parser.add_argument(
        "--count", "-n", type=int, default=5,
        help="Number of cases to generate (default: 5)",
    )
    parser.add_argument("--era", type=str, default=None, help="Force a specific era")
    parser.add_argument("--difficulty", type=int, default=None, help="Force difficulty (1-5)")
    parser.add_argument("--crime-type", type=str, default=None, help="Force crime type")
    args = parser.parse_args()

    logger.info(f"Starting batch generation of {args.count} cases...")
    results = asyncio.run(
        generate_batch(args.count, args.era, args.difficulty, args.crime_type)
    )

    logger.info(f"\n{'=' * 60}")
    logger.info(f"BATCH GENERATION COMPLETE: {len(results)}/{args.count} cases generated")
    logger.info(f"{'=' * 60}")
    for r in results:
        logger.info(f"  {r['case_number']} — \"{r['title']}\" (D:{r['difficulty']}, {r['era']})")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()
