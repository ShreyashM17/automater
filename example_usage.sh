#!/bin/bash

# Example usage script for Text Replacer Tool

echo "🚀 Text Replacer Tool - Example Usage"
echo "====================================="

# Example 1: Basic text replacement (auto-detects GitHub repo)
echo "Example 1: Basic text replacement (auto-detects GitHub repo)"
echo "python text_replacer.py ./my-project 'old text' 'new text'"
echo ""

# Example 2: With GitHub token from environment variable
echo "Example 2: With GitHub token from environment variable"
echo "export GITHUB_TOKEN=\"your_github_token\""
echo "python text_replacer.py ./my-project 'old text' 'new text'"
echo ""

# Example 3: Dry run to preview changes
echo "Example 3: Dry run to preview changes"
echo "python text_replacer.py ./my-project 'old text' 'new text' --dry-run"
echo ""

# Example 4: Target specific file extensions
echo "Example 4: Target specific file extensions"
echo "python text_replacer.py ./my-project 'TODO' 'FIXME' --extensions .py .js .ts"
echo ""

# Example 5: Use regex for pattern matching
echo "Example 5: Use regex for pattern matching"
echo "python text_replacer.py ./my-project 'version: \\d+\\.\\d+\\.\\d+' 'version: 2.0.0' --regex"
echo ""

# Example 6: Full workflow with GitHub PR (auto-detected repo)
echo "Example 6: Full workflow with GitHub PR (auto-detected repo)"
echo "export GITHUB_TOKEN=\"your_github_token\""
echo "python text_replacer.py ./my-project 'old text' 'new text' \\"
echo "  --branch \"update-text\" \\"
echo "  --pr-title \"Update text references\" \\"
echo "  --pr-description \"This PR updates text references across the codebase\""
echo ""

# Example 7: Custom commit message
echo "Example 7: Custom commit message"
echo "python text_replacer.py ./my-project 'old text' 'new text' \\"
echo "  --commit-message \"Update company name across all files\""
echo ""

echo "💡 Tips:"
echo "- Use --dry-run to preview changes before applying them"
echo "- Set GITHUB_TOKEN environment variable for easier PR creation"
echo "- Use --extensions to target specific file types"
echo "- Use --regex for complex pattern matching"
echo "- GitHub repo info is auto-detected from git remote (origin)"
echo ""

echo "🔧 Setup GitHub Token:"
echo "export GITHUB_TOKEN=\"your_github_token_here\""
echo ""

echo "📝 Configuration:"
echo "Use environment variables and command-line arguments for configuration"
echo ""

echo "🎯 Auto-Detection Features:"
echo "- GitHub repository owner and name from git remote"
echo "- Base branch for PR creation"
echo "- GitHub token from environment variable"
