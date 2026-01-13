#!/bin/bash
# Deploy public/ folder to gh-pages branch (incremental)

set -e

echo "🔨 Building site..."
.venv/bin/python build.py

echo "📦 Deploying to gh-pages..."

cd public

# Initialize if first time
if [ ! -d .git ]; then
git init
git remote add origin git@github.com:maxsheridan/blog.git
git fetch origin gh-pages || true
git reset --soft origin/gh-pages || true
else
# Clean any uncommitted changes and sync with remote
git reset --hard HEAD
git clean -fd
git fetch origin gh-pages
git reset --soft origin/gh-pages
fi

# Stage and commit only what changed
git add -A

if git diff --cached --quiet; then
echo "⚠️  No changes to deploy"
cd ..
exit 0
fi

git commit -m "Deploy site - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
git push origin HEAD:gh-pages

cd ..

echo "✨ Deployed successfully!"
echo "🌐 Site: https://maxsheridan.github.io/blog/"