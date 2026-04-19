"""
Fix markdown formatting issues across all .md files:
- ##Heading -> ## Heading (missing space after #)
- Remove trailing "Last updated X ago" lines
- Remove leftover TOC links at the end of files
- Clean up other common formatting issues
"""

import os
import re
import glob

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix headings missing space after #
    # Match lines starting with 1-6 # followed by a non-space, non-# character
    content = re.sub(r'^(#{1,6})([^\s#])', r'\1 \2', content, flags=re.MULTILINE)

    # Fix headings with emoji directly after # (e.g. ##🏠 -> ## 🏠)
    content = re.sub(r'^(#{1,6}) ?([^\s#])', r'\1 \2', content, flags=re.MULTILINE)

    # Remove "Last updated X ago" lines
    content = re.sub(r'^Last updated \d+ (?:months?|years?|days?|hours?|weeks?) ago.*$', '', content, flags=re.MULTILINE)

    # Remove leftover TOC anchor links at end of file (lines like "- [Section Name](#anchor)")
    lines = content.split('\n')
    # Find trailing TOC block
    end_idx = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped == '':
            continue
        if re.match(r'^- \[.+\]\(#.+\)$', stripped):
            end_idx = i
        else:
            break
    
    if end_idx < len(lines):
        lines = lines[:end_idx]
        content = '\n'.join(lines)

    # Clean up multiple trailing newlines
    content = content.rstrip() + '\n'

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    md_files = glob.glob(os.path.join(OUTPUT_DIR, '**', '*.md'), recursive=True)
    # Exclude helper scripts
    exclude = ['fix_headings.py', 'scrape_gitbook.py', 'cleanup_notes.py']
    md_files = [f for f in md_files if os.path.basename(f) not in exclude]

    print(f"Scanning {len(md_files)} markdown files...")

    modified = 0
    for filepath in sorted(md_files):
        rel = os.path.relpath(filepath, OUTPUT_DIR)
        if fix_file(filepath):
            modified += 1
            print(f"  Fixed: {rel}")

    print(f"\nDone! Fixed {modified} of {len(md_files)} files.")


if __name__ == '__main__':
    main()
