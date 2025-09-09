#!/usr/bin/env python3
"""
Text Replacer Web UI
A web interface for the text replacement tool.
"""

import os
import sys
import json
import re
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from text_replacer import TextReplacer

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variable to store job status
job_status = {}

class WebTextReplacer(TextReplacer):
    """Extended TextReplacer with web UI support."""
    
    def __init__(self, directory: str, github_token: str = None, repo_owner: str = None, repo_name: str = None):
        super().__init__(directory, github_token, repo_owner, repo_name)
        self.job_id = None
        self.status_callback = None
    
    def set_job_id(self, job_id: str):
        """Set job ID for status tracking."""
        self.job_id = job_id
    
    def set_status_callback(self, callback):
        """Set callback for status updates."""
        self.status_callback = callback
    
    def update_status(self, status: str, progress: int = None, details: str = None):
        """Update job status."""
        if self.job_id and self.status_callback:
            self.status_callback(self.job_id, status, progress, details)
    
    def find_files(self, pattern: str, file_extensions: list = None, 
                   max_files: int = 10000, exclude_dirs: list = None) -> list:
        """Find files with progress updates."""
        self.update_status("Searching files...", 10)
        
        matching_files = []
        files_checked = 0
        
        if exclude_dirs is None:
            exclude_dirs = ['.git', 'node_modules', 'dist', 'build', '.next', '__pycache__']
        
        # Get all files first
        all_files = []
        for file_path in self.directory.rglob('*'):
            if file_path.is_file():
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue
                if file_extensions and file_path.suffix not in file_extensions:
                    continue
                all_files.append(file_path)
                if len(all_files) >= max_files:
                    break
        
        total_files = len(all_files)
        self.update_status(f"Scanning {total_files} files...", 20)
        
        for file_path in all_files:
            files_checked += 1
            progress = 20 + int((files_checked / total_files) * 60)
            self.update_status(f"Checking file {files_checked}/{total_files}", progress)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if re.search(pattern, content, re.IGNORECASE):
                        matching_files.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                continue
        
        self.update_status(f"Found {len(matching_files)} matching files", 80)
        return matching_files
    
    def replace_text(self, search_pattern: str, replacement: str, 
                    file_extensions: list = None, use_regex: bool = False,
                    max_files: int = 10000, exclude_dirs: list = None, 
                    dry_run: bool = False) -> dict:
        """Replace text with progress updates."""
        self.update_status("Starting text replacement...", 0)
        
        try:
            matching_files = self.find_files(search_pattern, file_extensions, max_files, exclude_dirs)
        except Exception as e:
            self.update_status(f"Error during file search: {e}", 0, "error")
            return {"files_processed": 0, "total_replacements": 0, "files_changed": 0}
        
        if not matching_files:
            self.update_status("No files found containing the search pattern", 100)
            return {"files_processed": 0, "total_replacements": 0, "files_changed": 0}
        
        self.update_status(f"Processing {len(matching_files)} files...", 80)
        
        files_processed = 0
        total_replacements = 0
        files_changed = 0
        
        for i, file_path in enumerate(matching_files):
            progress = 80 + int((i / len(matching_files)) * 20)
            self.update_status(f"Processing {file_path.name}...", progress)
            
            changed, count = self.replace_in_file(file_path, search_pattern, replacement, use_regex, dry_run)
            files_processed += 1
            
            if changed:
                files_changed += 1
                total_replacements += count
                self.changes_made.append({
                    'file': str(file_path.relative_to(self.directory)),
                    'replacements': count
                })
        
        self.update_status("Text replacement completed!", 100)
        return {
            "files_processed": files_processed,
            "total_replacements": total_replacements,
            "files_changed": files_changed
        }

def update_job_status(job_id: str, status: str, progress: int = None, details: str = None):
    """Update job status in global dictionary."""
    job_status[job_id] = {
        'status': status,
        'progress': progress or 0,
        'details': details or '',
        'timestamp': time.time()
    }

def run_replacement_job(job_id: str, data: dict):
    """Run text replacement job in background thread."""
    try:
        # Initialize replacer
        replacer = WebTextReplacer(
            directory=data['directory'],
            github_token=data.get('github_token'),
            repo_owner=data.get('repo_owner'),
            repo_name=data.get('repo_name')
        )
        
        replacer.set_job_id(job_id)
        replacer.set_status_callback(update_job_status)
        
        # Run workflow
        if data.get('dry_run', False):
            result = replacer.replace_text(
                search_pattern=data['search'],
                replacement=data['replace'],
                file_extensions=data.get('extensions'),
                use_regex=data.get('use_regex', False),
                max_files=data.get('max_files', 10000),
                exclude_dirs=data.get('exclude_dirs'),
                dry_run=True
            )
            job_status[job_id]['result'] = result
            job_status[job_id]['status'] = 'completed'
        else:
            # Full workflow
            success = replacer.run_full_workflow(
                search_pattern=data['search'],
                replacement=data['replace'],
                file_extensions=data.get('extensions'),
                use_regex=data.get('use_regex', False),
                branch_name=data.get('branch'),
                commit_message=data.get('commit_message'),
                pr_title=data.get('pr_title'),
                pr_description=data.get('pr_description'),
                max_files=data.get('max_files', 10000),
                exclude_dirs=data.get('exclude_dirs')
            )
            job_status[job_id]['result'] = {'success': success}
            job_status[job_id]['status'] = 'completed' if success else 'failed'
            
    except Exception as e:
        job_status[job_id]['status'] = 'error'
        job_status[job_id]['error'] = str(e)

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_replacement():
    """Start text replacement job."""
    data = request.json
    
    # Generate job ID
    job_id = f"job_{int(time.time())}"
    
    # Start job in background thread
    thread = threading.Thread(target=run_replacement_job, args=(job_id, data))
    thread.daemon = True
    thread.start()
    
    # Initialize job status
    job_status[job_id] = {
        'status': 'started',
        'progress': 0,
        'details': 'Initializing...',
        'timestamp': time.time()
    }
    
    return jsonify({'job_id': job_id})

@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get job status."""
    if job_id not in job_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job_status[job_id])

@app.route('/api/validate-directory', methods=['POST'])
def validate_directory():
    """Validate directory path."""
    data = request.json
    directory = data.get('directory', '')
    
    if not directory:
        return jsonify({'valid': False, 'error': 'Directory path is required'})
    
    path = Path(directory).resolve()
    
    if not path.exists():
        return jsonify({'valid': False, 'error': 'Directory does not exist'})
    
    if not (path / '.git').exists():
        return jsonify({'valid': False, 'error': 'Directory is not a Git repository'})
    
    # Try to detect GitHub repo
    try:
        replacer = TextReplacer(str(path))
        if replacer.repo_owner and replacer.repo_name:
            return jsonify({
                'valid': True, 
                'repo_info': f"{replacer.repo_owner}/{replacer.repo_name}",
                'repo_owner': replacer.repo_owner,
                'repo_name': replacer.repo_name
            })
        else:
            return jsonify({'valid': True, 'repo_info': 'GitHub repo not detected'})
    except Exception as e:
        return jsonify({'valid': True, 'repo_info': f'Error detecting repo: {e}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
