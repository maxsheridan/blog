#!/bin/bash
# Deploy public/ folder to gh-pages branch

set -e

echo "🔨 Building site..."
.venv/bin/python build.py

echo "📦 Deploying to gh-pages..."
cd public
git init
git add -A
git commit -m "Deploy site - $(date '+%Y-%m-%d %H:%M:%S')"
git branch -M gh-pages
git remote add origin git@github.com:maxsheridan/blog.git 2>/dev/null || git remote set-url origin git@github.com:maxsheridan/blog.git
git push -f origin gh-pages
cd ..

echo "✨ Deployed successfully!"
echo "📝 Go to https://github.com/maxsheridan/blog/settings/pages"
echo "   Set source to: gh-pages branch, / (root)"
