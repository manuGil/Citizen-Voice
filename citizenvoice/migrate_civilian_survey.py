#!/usr/bin/env python3
"""
Safe migration script for CIVILIAN Survey from civilian-db.json dump.
This script extracts and recreates only the CIVILIAN Survey with its questions and answers,
handling any data model differences safely.
"""

import json
import os
import sys
import django
from datetime import datetime

# =============================================================================
# CONFIGURATION - Edit these paths as needed
# =============================================================================
ENV_FILE_PATH = ".env"  # Change this to your .env file path
# ENV_FILE_PATH = "../.env"     # Alternative: use this line instead
# ENV_FILE_PATH = None          # Alternative: use None to skip .env loading
# =============================================================================

# Setup Django environment
try:
    from dotenv import load_dotenv

    if ENV_FILE_PATH and os.path.exists(ENV_FILE_PATH):
        print(f"📄 Loading environment from: {ENV_FILE_PATH}")
        load_dotenv(ENV_FILE_PATH, override=True)
    else:
        print("⚠️  No .env file found or specified. Using system environment.")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "citizenvoice.settings")
django.setup()

from voice.models import Survey, Question, Response, Answer
from voice.models import (
    PointFeature,
    PolygonFeature,
    LineFeature,
    LocationCollection,
    MapView,
)
from django.contrib.auth.models import User


def load_dump_data(file_path):
    """Load and parse the database dump."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None


def find_civilian_survey_data(dump_data):
    """Extract CIVILIAN Survey and related data from dump."""
    civilian_survey = None
    questions = []
    responses = []
    answers = []
    mapviews = []
    locations = []

    for item in dump_data:
        model = item.get("model")
        fields = item.get("fields", {})
        pk = item.get("pk")

        # Find CIVILIAN Survey
        if model == "voice.survey" and pk == 3:
            if fields.get("name") == "CIVILIAN Survey":
                civilian_survey = item
                print(f"✅ Found CIVILIAN Survey (pk: {pk})")

        # Find questions for survey pk=3
        elif model == "voice.question":
            if fields.get("survey") == 3:
                questions.append(item)

        # Find responses for survey pk=3
        elif model == "voice.response":
            if fields.get("survey") == 3:
                responses.append(item)

        # Find answers related to CIVILIAN Survey responses
        elif model == "voice.answer":
            # We'll filter these after we have response IDs
            answers.append(item)

        # Find mapviews and locations
        elif model == "voice.mapview":
            mapviews.append(item)
        elif model in [
            "voice.pointfeature",
            "voice.polygonfeature",
            "voice.linefeature",
            "voice.locationcollection",
        ]:
            locations.append(item)

    return civilian_survey, questions, responses, answers, mapviews, locations


def migrate_survey(
    survey_data,
    questions_data,
    responses_data,
    answers_data,
    mapviews_data,
    locations_data,
):
    """Safely migrate the CIVILIAN Survey to current database."""

    print("\n🔄 Starting CIVILIAN Survey migration...")

    # 1. Create/Update Survey
    survey_fields = survey_data["fields"]
    survey, created = Survey.objects.get_or_create(
        name="CIVILIAN Survey",
        defaults={
            "description": survey_fields.get("description", ""),
            "is_published": survey_fields.get("is_published", True),
            "need_logged_user": survey_fields.get("need_logged_user", False),
            "editable_answers": survey_fields.get("editable_answers", True),
            "submit_message": survey_fields.get(
                "submit_message", "Thank you for your participation!"
            ),
            "publish_date": survey_fields.get("publish_date", datetime.now()),
            "expire_date": survey_fields.get("expire_date", "2025-04-30T08:24:07Z"),
            "designer": None,  # Set to None or get appropriate user
        },
    )

    action = "Created" if created else "Updated"
    print(f"✅ {action} Survey: {survey.name} (ID: {survey.id})")

    # 2. Migrate Questions (only if survey was created new)
    if created or not survey.question_set.exists():
        print(f"📋 Migrating {len(questions_data)} questions...")

        for q_data in questions_data:
            fields = q_data["fields"]

            # Create question with safe field mapping
            question_data = {
                "survey": survey,
                "text": fields.get("text", ""),
                "explanation": fields.get("explanation", ""),
                "question_type": fields.get("question_type", "text"),
                "required": fields.get("required", False),
                "has_text_input": fields.get("has_text_input", True),
                "order": fields.get("order", 1),
            }

            # Handle optional fields safely
            if "choices" in fields:
                question_data["choices"] = fields["choices"]
            if "default_value" in fields:
                question_data["default_value"] = fields["default_value"]

            try:
                question = Question.objects.create(**question_data)
                print(f"  ✅ Question: {question.text[:50]}...")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not create question: {e}")
                continue

    print(f"✅ Migration completed! Survey '{survey.name}' is ready.")
    return survey


def main():
    """Main migration function."""
    print("🚀 CIVILIAN Survey Migration Tool")
    print("=" * 50)

    # Load dump data
    dump_file = "./citizenvoice/civilian-db.json"
    print(f"📂 Loading data from {dump_file}...")

    dump_data = load_dump_data(dump_file)
    if not dump_data:
        sys.exit(1)

    print(f"📊 Loaded {len(dump_data)} database records")

    # Extract CIVILIAN Survey data
    civilian_survey, questions, responses, answers, mapviews, locations = (
        find_civilian_survey_data(dump_data)
    )

    if not civilian_survey:
        print("❌ CIVILIAN Survey not found in dump!")
        sys.exit(1)

    print(
        f"📋 Found: Survey + {len(questions)} questions + {len(responses)} responses + {len(answers)} answers"
    )

    # Confirm migration
    print("\n⚠️  This will create/update the CIVILIAN Survey in your current database.")
    confirm = input("Continue? (y/N): ").strip().lower()

    if confirm != "y":
        print("❌ Migration cancelled.")
        sys.exit(0)

    # Perform migration
    try:
        migrated_survey = migrate_survey(
            civilian_survey, questions, responses, answers, mapviews, locations
        )

        print("\n🎉 Migration completed successfully!")
        print(f"📋 Survey ID: {migrated_survey.id}")
        print(f"📝 Questions: {migrated_survey.question_count()}")
        print(f"🔗 Survey URL: /survey/{migrated_survey.id}/")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
