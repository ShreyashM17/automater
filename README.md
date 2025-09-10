# Text Replacer Tool

A powerful web-based tool that can find and replace text in files within a directory, automatically create a Git branch, commit changes, and raise a pull request on GitHub.

## Features

- 🎨 **Modern Web UI**: Beautiful dark mode interface with real-time progress tracking
- 🔍 **Smart Text Search**: Find text patterns across multiple files in a directory
- 🔄 **Flexible Replacement**: Replace text with exact matches or regex patterns
- 🌿 **Git Integration**: Automatically create branches and commit changes
- 🚀 **GitHub Integration**: Create pull requests automatically
- 📁 **File Filtering**: Target specific file extensions
- 🔍 **Dry Run Mode**: Preview changes before applying them
- ⚙️ **Advanced Options**: Comprehensive configuration options

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

### Command Line Interface (Basic)

For simple text replacement without Git operations:

```bash
# Basic replacement
python text_replacer.py /path/to/directory "old text" "new text"

# Dry run to preview changes
python text_replacer.py /path/to/directory "old text" "new text" --dry-run

# Limit number of files
python text_replacer.py /path/to/directory "old text" "new text" --max-files 1000
```

**Note**: For advanced features like Git operations, PR creation, and full workflow management, use the web UI.

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: Your GitHub personal access token for PR creation

### GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. Set the token as an environment variable:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

## How It Works

1. **Directory Selection**: Choose the directory containing your Git repository
2. **Text Search**: Enter the text pattern you want to find
3. **Replacement**: Specify the text to replace with
4. **Configuration**: Set advanced options like file extensions, exclusions, etc.
5. **Preview**: Use dry run mode to preview changes
6. **Execute**: Run the full workflow to make changes, create branch, commit, and raise PR

## File Structure

```
text_replacer/
├── app.py                 # Flask web application
├── text_replacer.py       # Core text replacement logic
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
├── static/
│   ├── css/
│   │   └── style.css     # Dark mode styles
│   └── js/
│       └── app.js        # Web UI JavaScript
└── templates/
    └── index.html        # Web UI template
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request