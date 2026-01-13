#!/bin/bash
# Deploy public/ folder to gh-pages branch

set -e

echo "🔨 Building site..."
.venv/bin/python build.py

echo "📦 Deploying to gh-pages..."

cd public

# Clean up any existing git repository
rm -rf .git

# Initialize fresh repository
git init
git add -A
git commit -m "Deploy site - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
git branch -M gh-pages
git remote add origin git@github.com:maxsheridan/blog.git
git push -f origin gh-pages

cd ..

echo "✨ Deployed successfully!"
echo "🌐 Site: https://maxsheridan.github.io/blog/"