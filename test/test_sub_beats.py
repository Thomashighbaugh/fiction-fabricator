#!/usr/bin/env python3
"""
Test script to demonstrate sub-beat generation feature.
This shows the new hierarchy: Chapter -> Plot Beats -> Sub-Beats -> Content
"""
import xml.etree.ElementTree as ET

def create_test_structure():
    """Create a sample XML structure demonstrating the sub-beat hierarchy."""
    
    book = ET.Element('book')
    title = ET.SubElement(book, 'title')
    title.text = 'The Lost Crystal'
    
    chapters = ET.SubElement(book, 'chapters')
    
    chapter = ET.SubElement(chapters, 'chapter', id='1', setting='Ancient ruins deep in the forest')
    chapter_number = ET.SubElement(chapter, 'number')
    chapter_number.text = '1'
    chapter_title = ET.SubElement(chapter, 'title')
    chapter_title.text = 'Discovery'
    chapter_summary = ET.SubElement(chapter, 'summary')
    chapter_summary.text = 'Ethan discovers ancient ruins with mysterious crystals.'
    
    # Content tag (empty, to be filled later)
    content = ET.SubElement(chapter, 'content')
    
    # Plot beats
    plot_beats = ET.SubElement(chapter, 'plot_beats')
    
    # Beat 1: Ethan explores the forest
    beat1 = ET.SubElement(plot_beats, 'beat')
    beat1.text = 'Ethan explores the deep forest, feeling drawn toward an unknown destination.'
    
    # Sub-beats for beat 1 (each representing 2-3 paragraphs)
    sub_beats1 = ET.SubElement(beat1, 'sub_beats')
    sub_beat1_1 = ET.SubElement(sub_beats1, 'sub_beat')
    sub_beat1_1.text = 'Ethan walks through the forest, describing the atmosphere and his growing sense of unease.'
    sub_beat1_2 = ET.SubElement(sub_beats1, 'sub_beat')
    sub_beat1_2.text = 'He notices strange glowing fungi and ancient trees, wondering what lies deeper in the woods.'
    sub_beat1_3 = ET.SubElement(sub_beats1, 'sub_beat')
    sub_beat1_3.text = 'A pull draws him forward, his curiosity overcoming his hesitation as he ventures into unknown territory.'
    
    # Beat 2: Ethan finds the ruins
    beat2 = ET.SubElement(plot_beats, 'beat')
    beat2.text = 'Ethan stumbles upon ancient stone ruins covered in glowing crystals.'
    
    # Sub-beats for beat 2
    sub_beats2 = ET.SubElement(beat2, 'sub_beats')
    sub_beat2_1 = ET.SubElement(sub_beats2, 'sub_beat')
    sub_beat2_1.text = 'The trees part suddenly, revealing crumbling stone structures half-buried in moss and vines.'
    sub_beat2_2 = ET.SubElement(sub_beats2, 'sub_beat')
    sub_beat2_2.text = 'Crystals embedded in the stones pulse with soft blue light, responding to Ethan\'s presence.'
    sub_beat2_3 = ET.SubElement(sub_beats2, 'sub_beat')
    sub_beat2_3.text = 'Ethan approaches cautiously, his heart racing as he realizes he\'s found something truly ancient.'
    
    # Beat 3: Ethan discovers a key chamber
    beat3 = ET.SubElement(plot_beats, 'beat')
    beat3.text = 'Ethan discovers a hidden chamber with a central pedestal.'
    
    # Sub-beats for beat 3
    sub_beats3 = ET.SubElement(beat3, 'sub_beats')
    sub_beat3_1 = ET.SubElement(sub_beats3, 'sub_beat')
    sub_beat3_1.text = 'Following the crystal light, Ethan finds a doorway leading underground into darkness.'
    sub_beat3_2 = ET.SubElement(sub_beats3, 'sub_beat')
    sub_beat3_2.text = 'He creates a light source and descends into a vast chamber filled with more crystals.'
    sub_beat3_3 = ET.SubElement(sub_beats3, 'sub_beat')
    sub_beat3_3.text = 'In the center stands a pedestal with an unusual crystal, pulsing brighter than all the others.'
    
    return book

def print_structure(element, indent=0):
    """Recursively print the XML structure."""
    prefix = '  ' * indent
    if element.text and element.text.strip():
        print(f'{prefix}{element.tag}: "{element.text.strip()[:50]}..."')
    else:
        print(f'{prefix}{element.tag}')
    
    for child in element:
        print_structure(child, indent + 1)

def main():
    print("=" * 70)
    print("SUB-BEAT GENERATION FEATURE DEMONSTRATION")
    print("=" * 70)
    print()
    print("New Hierarchy:")
    print("  1. Plot (Initial Idea)")
    print("  2. Chapters (with summaries)")
    print("  3. Plot Beats (major plot events)")
    print("  4. Sub-Beats (each = 2-3 paragraphs) <-- NEW!")
    print("  5. Content (actual prose)")
    print()
    print("=" * 70)
    print("Sample XML Structure:")
    print("=" * 70)
    print()
    
    book = create_test_structure()
    
    # Pretty print the structure
    xml_str = ET.tostring(book, encoding='unicode')
    
    # Format nicely
    def indent_xml(elem, level=0):
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subchild in elem:
                indent_xml(subchild, level + 1)
            if len(elem) > 0:
                last_child = list(elem)[-1]
                if not last_child.tail or not last_child.tail.strip():
                    last_child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem
    
    indent_xml(book)
    print(ET.tostring(book, encoding='unicode'))
    print()
    print("=" * 70)
    print("Benefits of Sub-Beats:")
    print("=" * 70)
    print("  • Better word count on first pass (each sub-beat = 2-3 paragraphs)")
    print("  • More granular guidance for LLM")
    print("  • Consistent pacing throughout chapters")
    print("  • Reduces need for multiple expansion passes")
    print("  • Each beat gets proper development (3-5 sub-beats × 2-3 paragraphs = 6-15 paragraphs per beat)")
    print()
    print("Example Calculation:")
    print("  • Chapter with 5 plot beats")
    print("  • Each beat has 3-4 sub-beats")
    print("  • Each sub-beat = 2-3 paragraphs")
    print("  • Total: 5 beats × 3.5 sub-beats × 2.5 paragraphs ≈ 44 paragraphs")
    print("  • At ~50 words/paragraph: ~2200+ words per chapter")
    print()

if __name__ == '__main__':
    main()
