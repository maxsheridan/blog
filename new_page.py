#!/usr/bin/env python3
"""
Script to create a new blank page with proper frontmatter.
"""
import os
import sys


def create_new_page(filename):
    """Create a new blank page with frontmatter."""
    pages_dir = "content/pages"
    
    # Ensure pages directory exists
    os.makedirs(pages_dir, exist_ok=True)
    
    # Ensure filename has .md extension
    if not filename.endswith(".md"):
        filename += ".md"
    
    filepath = os.path.join(pages_dir, filename)
    
    # Check if file already exists
    if os.path.exists(filepath):
        print(f"Error: File {filepath} already exists!")
        return False
    
    # Create page template
    template = """---
title: 
---

"""
    
    # Write the file
    with open(filepath, "w") as f:
        f.write(template)
    
    print(f"✓ Created new page: {filepath}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a filename for the new page.")
        sys.exit(1)
    
    create_new_page(sys.argv[1])
