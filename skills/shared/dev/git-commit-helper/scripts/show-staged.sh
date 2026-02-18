#!/bin/bash
# Show staged changes for commit message analysis

echo "=== Staged files ==="
git status --short | grep "^[AMDRC]"

echo ""
echo "=== Diff statistics ==="
git diff --staged --stat

echo ""
echo "=== Detailed diff ==="
git diff --staged
