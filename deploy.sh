#!/bin/bash
# Deploy public/ folder to gh-pages branch (incremental, fast)

set -e

echo "🔨 Building site..."
.venv/bin/python build.py

echo "📦 Deploying to gh-pages..."

cd public

# If this is the first deploy, initialize once
if [ ! -d .git ]; then
git init
git remote add origin git@github.com:maxsheridan/blog.git
fi

# Fetch existing gh-pages history
git fetch origin gh-pages || true
git checkout -B gh-pages origin/gh-pages 2>/dev/null || git checkout -B gh-pages

git add -A

# Avoid empty commits
if git diff --cached --quiet; then
echo "⚠️  No changes to deploy"
cd ..
exit 0
fi

git commit -m "Deploy site - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
git push origin gh-pages

cd ..

echo "✨ Deployed successfully!"