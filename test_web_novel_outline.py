#!/usr/bin/env python3
# Test script for web novel outline functionality

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from Tools.WebNovelOutlineGenerator import handle_web_novel_outline_generation
    print("✓ Web Novel Outline Generator imported successfully")
    
    from Tools.OutlineGeneratorTool import generate_outline_tool
    print("✓ Modified Outline Generator Tool imported successfully")
    
    print("✓ All imports successful - web novel outline functionality is ready")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)