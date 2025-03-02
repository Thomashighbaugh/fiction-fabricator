# utils/data_validation.py
"""
Utility functions for data validation.

This module is designed to house custom data validation functions
that go beyond the basic validation provided by Pydantic. It's 
intended to encapsulate more complex or application-specific 
validation logic, ensuring data integrity and consistency 
within the Fiction Fabricator application.
"""

from typing import List, Dict, Any
from utils.logger import logger


def validate_scene_outline_consistency(
    chapter_outlines: List[Dict[str, Any]],
    scene_outlines: Dict[int, List[Dict[str, Any]]],
) -> bool:
    """
    Validates consistency between chapter outlines and scene outlines.

    Checks:
    1.  That every chapter number referenced in `scene_outlines` has a
        corresponding entry in `chapter_outlines`.
    2.  That scene numbers within each chapter are sequential and start from 1.
    """
    consistent = True
    chapter_numbers = {co["chapter_number"] for co in chapter_outlines}

    for chapter_num, scenes in scene_outlines.items():
        if chapter_num not in chapter_numbers:
            logger.warning(
                "Scene outlines exist for chapter %s, but no corresponding chapter outline found.",
                chapter_num,
            )
            consistent = False

        expected_scene_num = 1
        for scene in scenes:
            if scene["scene_number"] != expected_scene_num:
                logger.warning(
                    "Scene number mismatch in chapter %s. Expected %s, got %s.",
                    chapter_num,
                    expected_scene_num,
                    scene["scene_number"],
                )
                consistent = False
            expected_scene_num += 1
    return consistent


def validate_scene_part_text_structure(
    scene_parts_text: Dict[int, Dict[int, Dict[int, str]]]
) -> bool:
    """
    Validates structure of the scene_parts_text
    """
    consistent = True

    if not isinstance(scene_parts_text, dict):
        logger.error("Scene_parts_text is not a dictionary")
        return False

    for chapter_num, chapter_data in scene_parts_text.items():
        if not isinstance(chapter_num, int):
            logger.warning(
                "scene_parts_text chapter number is not an int: %s", type(chapter_num)
            )
            consistent = False

        if not isinstance(chapter_data, dict):
            logger.warning(
                "scene_parts_text chapter data is not a dict: %s", type(chapter_data)
            )
            consistent = False
            continue

        for scene_num, scene_data in chapter_data.items():
            if not isinstance(scene_num, int):
                logger.warning(
                    "scene_parts_text scene number is not an int: %s", type(scene_num)
                )
                consistent = False

            if not isinstance(scene_data, dict):
                logger.warning(
                    "scene_parts_text scene data is not a dict: %s", type(scene_data)
                )
                consistent = False
                continue

            for part_num, part_text in scene_data.items():
                if not isinstance(part_num, int):
                    logger.warning(
                        "scene_parts_text part number is not an int: %s", type(part_num)
                    )
                    consistent = False

                if not isinstance(part_text, str):
                    logger.warning(
                        "scene_parts_text part data is not a string: %s",
                        type(part_text),
                    )
                    consistent = False

    return consistent
