#!/usr/bin/env python3
# Test script for scene-based generation system

import os
import sys
import tempfile

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all scene-based components can be imported."""
    try:
        from Writer.Scene.SceneFileManager import SceneFileManager
        print("✓ SceneFileManager imported successfully")
        
        from Writer.Scene.ChapterByScene import ChapterByScene
        print("✓ Enhanced ChapterByScene imported successfully")
        
        from Writer.Chapter.ChapterGenerator import GenerateChapter
        print("✓ Enhanced ChapterGenerator imported successfully")
        
        from Tools.NovelWriter import write_novel
        print("✓ Enhanced NovelWriter imported successfully")
        
        from Tools.ShortStoryWriter import write_short_story
        print("✓ Enhanced ShortStoryWriter imported successfully")
        
        from Tools.WebNovelWriter import write_web_novel_chapter
        print("✓ Enhanced WebNovelWriter imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_scene_file_manager():
    """Test SceneFileManager functionality."""
    try:
        from Writer.Scene.SceneFileManager import SceneFileManager
        from Writer.PrintUtils import Logger
        from Writer.NarrativeContext import NarrativeContext, ChapterContext, SceneContext
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = Logger()
            file_manager = SceneFileManager(logger, temp_dir, "test_story")
            
            # Create mock scene context
            scene_context = SceneContext(scene_number=1, initial_outline="Test scene outline")
            scene_context.add_piece("This is a test scene content.", "Scene summary")
            scene_context.set_final_summary("Test scene final summary")
            
            # Test scene file creation
            scene_file = file_manager.save_scene_file(scene_context, 1, 10)
            if scene_file and os.path.exists(scene_file):
                print("✓ Scene file creation works")
            else:
                print("✗ Scene file creation failed")
                return False
            
            # Create mock chapter context
            chapter_context = ChapterContext(chapter_number=1, initial_outline="Test chapter outline")
            chapter_context.set_generated_content("This is test chapter content.")
            chapter_context.set_summary("Test chapter summary")
            chapter_context.add_scene(scene_context)
            
            # Test chapter file creation
            chapter_file = file_manager.stitch_chapter_from_scenes(chapter_context)
            if chapter_file and os.path.exists(chapter_file):
                print("✓ Chapter file stitching works")
            else:
                print("✗ Chapter file stitching failed")
                return False
            
            # Create mock narrative context
            narrative_context = NarrativeContext(initial_prompt="Test prompt", style_guide="Test style")
            narrative_context.story_type = "test"
            narrative_context.add_chapter(chapter_context)
            
            # Test book file creation
            book_file = file_manager.stitch_book_from_chapters(narrative_context, "Test Book")
            if book_file and os.path.exists(book_file):
                print("✓ Book file stitching works")
            else:
                print("✗ Book file stitching failed")
                return False
            
            # Test generation report
            report_file = file_manager.create_generation_report(narrative_context)
            if report_file and os.path.exists(report_file):
                print("✓ Generation report creation works")
            else:
                print("✗ Generation report creation failed")
                return False
            
            print("✓ All SceneFileManager tests passed")
            return True
            
    except Exception as e:
        print(f"✗ SceneFileManager test error: {e}")
        return False

def main():
    print("Testing Scene-Based Generation System...")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports...")
    if not test_imports():
        print("Import tests failed!")
        return False
    
    # Test SceneFileManager
    print("\n2. Testing SceneFileManager...")
    if not test_scene_file_manager():
        print("SceneFileManager tests failed!")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! Scene-based generation system is ready.")
    print("\nKey improvements implemented:")
    print("- Individual scene files for error resilience")
    print("- Scene-by-scene critique and revision")
    print("- Chapter stitching from scenes")
    print("- Complete book assembly from chapters")
    print("- Detailed generation reports")
    print("- Enhanced error recovery capabilities")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)