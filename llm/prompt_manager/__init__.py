# llm/prompt_manager/__init__.py

"""
Package initializer for the prompt_manager package.

This package is dedicated to managing and organizing prompts for
the Fiction Fabricator application. It includes modules for:

- base_prompts.py: Defines common prompt templates and potentially 
  utility functions shared across different prompt modules.
- book_spec_prompts.py: Contains prompt templates specifically for 
  generating and enhancing BookSpec objects.
- plot_outline_prompts.py: Contains prompt templates for generating and 
  enhancing PlotOutline objects.
- chapter_outline_prompts.py: Contains prompt templates for generating and 
  enhancing ChapterOutline objects.
- scene_outline_prompts.py: Contains prompt templates for generating and 
  enhancing SceneOutline objects.
- scene_part_prompts.py: Contains prompt templates for generating and 
  enhancing ScenePart objects.

Each module within this package is responsible for encapsulating the 
prompts related to a specific content generation stage, promoting 
organization and maintainability of the prompt engineering aspects 
of the application.
"""