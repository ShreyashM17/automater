# Text Replacer Tool

A powerful command-line tool that can find and replace text in files within a directory, automatically create a Git branch, commit changes, and raise a pull request on GitHub.

## Features

- 🔍 **Smart Text Search**: Find text patterns across multiple files in a directory
- 🔄 **Flexible Replacement**: Replace text with exact matches or regex patterns
- 🌿 **Git Integration**: Automatically create branches and commit changes
- 🚀 **GitHub Integration**: Create pull requests automatically
- 📁 **File Filtering**: Target specific file extensions
- 🔍 **Dry Run Mode**: Preview changes before applying them
- ⚙️ **Configurable**: Use configuration files for default settings

## Installation

### Prerequisites

- Python 3.7 or higher
- Git installed and configured
- GitHub repository access (for PR creation)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Web UI (Recommended)

The easiest way to use the tool is through the web interface:

```bash
python app.py
```

Then open your browser and go to `http://localhost:5001`

#### Web UI Features

- 🎨 **Modern Interface**: Clean, responsive design with real-time progress tracking
- 📁 **Directory Validation**: Automatic validation of Git repositories
- ⚙️ **Advanced Options**: Easy access to all configuration options
- 🔍 **Dry Run Mode**: Preview changes before applying them
- 📊 **Real-time Progress**: Live updates on job status and progress
- 💾 **Settings Persistence**: Automatically saves your preferences
- 🔔 **Notifications**: Toast notifications for important events
- 📱 **Mobile Friendly**: Works on desktop, tablet, and mobile devices

### Command Line Interface

For command-line usage, see the CLI section below.

## CLI Usage

### Basic Usage (Auto-detects GitHub repo)

```bash
python text_replacer.py /path/to/directory "old text" "new text"
```

### With GitHub Token from Environment Variable

```bash
export GITHUB_TOKEN="your_github_token"
python text_replacer.py /path/to/directory "old text" "new text"
```

### Advanced Usage

```bash
python text_replacer.py /path/to/directory "old text" "new text" \
  --extensions .py .js .ts \
  --regex \
  --branch "feature/text-replacement" \
  --commit-message "Update text across codebase" \
  --pr-title "Update text references" \
  --pr-description "This PR updates text references across the codebase"
```

### Dry Run Mode

Preview changes without making them:

```bash
python text_replacer.py /path/to/directory "old text" "new text" --dry-run
```

## Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `directory` | Directory to process | Yes |
| `search` | Text pattern to search for | Yes |
| `replace` | Text to replace with | Yes |
| `--extensions` | File extensions to process (e.g., .py .js .ts) | No |
| `--regex` | Use regex for search pattern | No |
| `--branch` | Branch name (auto-generated if not provided) | No |
| `--commit-message` | Commit message | No |
| `--pr-title` | PR title | No |
| `--pr-description` | PR description | No |
| `--github-token` | GitHub token for PR creation (or set GITHUB_TOKEN env var) | No |
| `--repo-owner` | GitHub repository owner (auto-detected from git remote) | No |
| `--repo-name` | GitHub repository name (auto-detected from git remote) | No |
| `--dry-run` | Show what would be changed without making changes | No |

## Configuration

The tool uses environment variables and command-line arguments for configuration. No additional config files are needed.

## Examples

### Example 1: Simple Text Replacement

```bash
python text_replacer.py ./my-project "old company name" "new company name"
```

### Example 2: Regex Replacement

```bash
python text_replacer.py ./my-project "version: \d+\.\d+\.\d+" "version: 2.0.0" --regex
```

### Example 3: Target Specific Files

```bash
python text_replacer.py ./my-project "TODO" "FIXME" --extensions .py .js
```

### Example 4: Full Workflow with PR (Auto-detected repo)

```bash
export GITHUB_TOKEN="your_github_token"
python text_replacer.py ./my-project "old text" "new text" \
  --branch "update-text" \
  --pr-title "Update text references"
```

## Workflow

The tool follows this workflow:

1. **Validation**: Checks if the directory exists and is a Git repository
2. **Branch Creation**: Creates a new branch (or uses existing uncommitted changes)
3. **Text Search**: Finds all files containing the search pattern
4. **Text Replacement**: Replaces the text in matching files
5. **Commit**: Commits the changes with a descriptive message
6. **Push**: Pushes the branch to the remote repository
7. **Pull Request**: Creates a pull request on GitHub (if credentials provided)

## Safety Features

- **Dry Run Mode**: Preview changes before applying them
- **Git Integration**: All changes are tracked in Git
- **Branch Isolation**: Changes are made in a separate branch
- **Detailed Logging**: See exactly what changes are being made
- **Error Handling**: Graceful handling of file access errors

## Error Handling

The tool handles various error conditions:

- Directory doesn't exist
- Not a Git repository
- File access permissions
- Git command failures
- GitHub API errors
- Network connectivity issues

## Requirements

- Python 3.7+
- Git
- requests library
- GitHub access (for PR creation)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
