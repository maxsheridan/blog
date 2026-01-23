#!/usr/bin/env python3
"""
Script to create a new blank blog post with proper frontmatter.
"""
import os
import sys
from datetime import datetime


def get_next_post_number():
    """Find the highest numbered post and return the next number."""
    posts_dir = "content/posts"
    if not os.path.exists(posts_dir):
        return 1
    
    post_files = [f for f in os.listdir(posts_dir) if f.startswith("post-") and f.endswith(".md")]
    if not post_files:
        return 1
    
    numbers = []
    for filename in post_files:
        try:
            num = int(filename.replace("post-", "").replace(".md", ""))
            numbers.append(num)
        except ValueError:
            continue
    
    return max(numbers) + 1 if numbers else 1


def create_new_post(filename=None):
    """Create a new blank post with frontmatter."""
    posts_dir = "content/posts"
    
    # Ensure posts directory exists
    os.makedirs(posts_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        post_num = get_next_post_number()
        filename = f"post-{post_num:02d}.md"
    elif not filename.endswith(".md"):
        filename += ".md"
    
    filepath = os.path.join(posts_dir, filename)
    
    # Check if file already exists
    if os.path.exists(filepath):
        print(f"Error: File {filepath} already exists!")
        return False
    
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create post template
    template = f"""---
title: 
subtitle: 
date: {today}
category: 
---

"""
    
    # Write the file
    with open(filepath, "w") as f:
        f.write(template)
    
    print(f"✓ Created new post: {filepath}")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom filename provided
        create_new_post(sys.argv[1])
    else:
        # Auto-generate filename
        create_new_post()