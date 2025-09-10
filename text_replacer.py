"""
Text Replacer Tool
A tool to find and replace text in files within a directory, create a Git branch, and raise a PR.
"""

import os
import argparse
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
import requests
from datetime import datetime


class TextReplacer:
  def __init__(self, directory: str, github_token: str = None, repo_owner: str = None, repo_name: str = None):
    self.directory = Path(directory).resolve()
    self.github_token = github_token or os.getenv('GITHUB_TOKEN')
    self.repo_owner = repo_owner
    self.repo_name = repo_name
    self.branch_name = None
    self.changes_made = []
    
    # Auto-detect GitHub repository info if not provided
    if not self.repo_owner or not self.repo_name:
      self._detect_github_repo()
  
  def _detect_github_repo(self) -> None:
    """Auto-detect GitHub repository owner and name from git remote."""
    try:
      # Get the remote URL
      result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                cwd=self.directory, capture_output=True, text=True)
      if result.returncode != 0:
        print("Warning: Could not detect GitHub repository from git remote.")
        return
      
      remote_url = result.stdout.strip()
      
      # Parse different URL formats
      if remote_url.startswith('https://github.com/'):
        # HTTPS format: https://github.com/owner/repo.git
        parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
        if len(parts) >= 2:
          self.repo_owner = parts[0]
          self.repo_name = parts[1]
          print(f"Detected GitHub repository: {self.repo_owner}/{self.repo_name}")
      elif remote_url.startswith('git@github.com:'):
        # SSH format: git@github.com:owner/repo.git
        parts = remote_url.replace('git@github.com:', '').replace('.git', '').split('/')
        if len(parts) >= 2:
          self.repo_owner = parts[0]
          self.repo_name = parts[1]
          print(f"Detected GitHub repository: {self.repo_owner}/{self.repo_name}")
      else:
        print(f"Warning: Unsupported remote URL format: {remote_url}")
        
    except Exception as e:
      print(f"Warning: Could not detect GitHub repository: {e}")
  
  def _get_current_branch(self) -> str:
    """Get the current branch name."""
    try:
      result = subprocess.run(['git', 'branch', '--show-current'], 
                cwd=self.directory, capture_output=True, text=True)
      if result.returncode == 0:
        return result.stdout.strip()
    except Exception:
      pass
    return "main"  # fallback
  
  def validate_directory(self) -> bool:
    """Validate that the directory exists and is a Git repository."""
    if not self.directory.exists():
      print(f"Error: Directory {self.directory} does not exist.")
      return False
      
    if not (self.directory / '.git').exists():
      print(f"Error: {self.directory} is not a Git repository.")
      return False
      
    return True
  
  def find_files(self, pattern: str, file_extensions: List[str] = None, 
         max_files: int = 10000, exclude_dirs: List[str] = None) -> List[Path]:
    """Find files containing the search pattern."""
    matching_files = []
    files_checked = 0
    
    if exclude_dirs is None:
      exclude_dirs = ['.git', 'node_modules', 'dist', 'build', '.next', '__pycache__']
    
    # Get all files first
    all_files = []
    for file_path in self.directory.rglob('*'):
      if file_path.is_file():
        # Skip .git directory and other hidden directories
        if any(part.startswith('.') for part in file_path.parts):
          continue
        
        # Skip excluded directories
        if any(excluded in str(file_path) for excluded in exclude_dirs):
          continue
          
        # Filter by file extensions if specified
        if file_extensions and file_path.suffix not in file_extensions:
          continue
          
        all_files.append(file_path)
        
        # Limit number of files to prevent hanging on very large repos
        if len(all_files) >= max_files:
          print(f"⚠️  Reached maximum file limit ({max_files}). Use --max-files to increase limit.")
          break
    
    total_files = len(all_files)
    print(f"Scanning {total_files} files for pattern...")
    
    for file_path in all_files:
      files_checked += 1
      
      # Show progress every 100 files
      if files_checked % 100 == 0 or files_checked == total_files:
        print(f"  Progress: {files_checked}/{total_files} files checked...")
      
      try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
          content = f.read()
          if re.search(pattern, content, re.IGNORECASE):
            matching_files.append(file_path)
      except (UnicodeDecodeError, PermissionError):
        # Skip binary files or files we can't read
        continue
          
    return matching_files
  
  def replace_in_file(self, file_path: Path, search_pattern: str, replacement: str, 
           use_regex: bool = False, dry_run: bool = False) -> Tuple[bool, int]:
    """Replace text in a single file."""
    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
      original_content = content
      
      if use_regex:
        content = re.sub(search_pattern, replacement, content, flags=re.IGNORECASE)
      else:
        content = content.replace(search_pattern, replacement)
      
      if content != original_content:
        if not dry_run:
          with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Count occurrences
        count = len(re.findall(re.escape(search_pattern), original_content, re.IGNORECASE))
        return True, count
      else:
        return False, 0
        
    except Exception as e:
      print(f"Error processing {file_path}: {e}")
      return False, 0
  
  def replace_text(self, search_pattern: str, replacement: str, 
          file_extensions: List[str] = None, use_regex: bool = False,
          max_files: int = 10000, exclude_dirs: List[str] = None, 
          dry_run: bool = False) -> Dict:
    """Replace text in all matching files."""
    print(f"Searching for pattern: '{search_pattern}'")
    print(f"Replacement: '{replacement}'")
    print(f"File extensions: {file_extensions or 'All'}")
    print(f"Use regex: {use_regex}")
    print("-" * 50)
    
    try:
      # Find files containing the pattern
      matching_files = self.find_files(search_pattern, file_extensions, max_files, exclude_dirs)
    except KeyboardInterrupt:
      print("\n⚠️  Search interrupted by user. Exiting...")
      return {"files_processed": 0, "total_replacements": 0, "files_changed": 0}
    except Exception as e:
      print(f"❌ Error during file search: {e}")
      return {"files_processed": 0, "total_replacements": 0, "files_changed": 0}
    
    if not matching_files:
      print("No files found containing the search pattern.")
      return {"files_processed": 0, "total_replacements": 0, "files_changed": 0}
    
    print(f"Found {len(matching_files)} files containing the pattern:")
    for file_path in matching_files:
      print(f"  - {file_path.relative_to(self.directory)}")
    print("-" * 50)
    
    # Process each file
    files_processed = 0
    total_replacements = 0
    files_changed = 0
    
    for file_path in matching_files:
      print(f"Processing: {file_path.relative_to(self.directory)}")
      changed, count = self.replace_in_file(file_path, search_pattern, replacement, use_regex, dry_run)
      
      files_processed += 1
      if changed:
        files_changed += 1
        total_replacements += count
        self.changes_made.append({
          'file': str(file_path.relative_to(self.directory)),
          'replacements': count
        })
        print(f"  ✓ Made {count} replacement(s) in {file_path.relative_to(self.directory)}")
      else:
        print(f"  - No changes needed in {file_path.relative_to(self.directory)}")
    
    print("-" * 50)
    print(f"Summary: {files_processed} files processed, {files_changed} files changed, {total_replacements} total replacements")
    
    return {
      "files_processed": files_processed,
      "total_replacements": total_replacements,
      "files_changed": files_changed
    }
  
  def create_branch(self, branch_name: str = None, interactive: bool = True) -> bool:
    """Create a new Git branch."""
    if not branch_name:
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      branch_name = f"text-replace-{timestamp}"
    
    self.branch_name = branch_name
    
    try:
      # Get current branch name
      current_branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                        cwd=self.directory, capture_output=True, text=True)
      current_branch = current_branch_result.stdout.strip()
      
      # Safety check: Don't allow operations on master/main branch
      if current_branch in ['master', 'main']:
        print(f"⚠️  WARNING: You are currently on the '{current_branch}' branch!")
        print("This tool will create a new branch to avoid modifying the main branch.")
        
        if interactive:
          print("If you want to proceed, the tool will create a new branch for your changes.")
          response = input("Do you want to continue? (y/N): ").strip().lower()
          if response != 'y':
            print("Operation cancelled to protect the main branch.")
            return False
        else:
          print("Proceeding to create a new branch for your changes...")
      
      # Check if we're on a clean working directory
      result = subprocess.run(['git', 'status', '--porcelain'], 
                cwd=self.directory, capture_output=True, text=True)
      
      if result.stdout.strip():
        print("Working directory has uncommitted changes. Committing them first...")
        subprocess.run(['git', 'add', '.'], cwd=self.directory, check=True)
        
        # Check if there are staged changes before committing
        staged_result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                      cwd=self.directory, capture_output=True, text=True)
        if staged_result.stdout.strip():
          subprocess.run(['git', 'commit', '-m', 'Auto-commit before text replacement'], 
                cwd=self.directory, check=True)
        else:
          print("No staged changes to commit.")
      
      # Create and checkout new branch
      subprocess.run(['git', 'checkout', '-b', branch_name], cwd=self.directory, check=True)
      print(f"Created and switched to branch: {branch_name}")
      return True
      
    except subprocess.CalledProcessError as e:
      print(f"Error creating branch: {e}")
      # Try to get more details about the error
      try:
        result = subprocess.run(['git', 'status'], cwd=self.directory, 
                  capture_output=True, text=True)
        print(f"Git status: {result.stdout}")
      except:
        pass
      return False
  
  def commit_changes(self, commit_message: str = None) -> bool:
    """Commit the changes made."""
    if not commit_message:
      commit_message = f"Replace text: {len(self.changes_made)} files modified"
    
    try:
      print(f"Attempting to commit with message: {commit_message}")
      
      # Check if there are any changes to commit
      result = subprocess.run(['git', 'status', '--porcelain'], 
                cwd=self.directory, capture_output=True, text=True)
      
      print(f"Git status before add: {result.stdout}")
      
      if not result.stdout.strip():
        print("No changes to commit.")
        return True
      
      # Add all changes
      print("Adding all changes to git...")
      subprocess.run(['git', 'add', '.'], cwd=self.directory, check=True)
      
      # Check if there are staged changes
      result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                cwd=self.directory, capture_output=True, text=True)
      
      print(f"Staged changes: {result.stdout}")
      
      if not result.stdout.strip():
        print("No staged changes to commit.")
        return True
      
      # Commit changes
      print("Committing changes...")
      subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.directory, check=True)
      print(f"Committed changes: {commit_message}")
      return True
      
    except subprocess.CalledProcessError as e:
      print(f"Error committing changes: {e}")
      # Try to get more details about the error
      try:
        result = subprocess.run(['git', 'status'], cwd=self.directory, 
                  capture_output=True, text=True)
        print(f"Git status: {result.stdout}")
        
        # Also check what's in the index
        result = subprocess.run(['git', 'diff', '--cached', '--stat'], 
                  cwd=self.directory, capture_output=True, text=True)
        print(f"Staged changes stat: {result.stdout}")
      except:
        pass
      return False
  
  def push_branch(self) -> bool:
    """Push the branch to remote."""
    try:
      # First try to set upstream and push
      subprocess.run(['git', 'push', '--set-upstream', 'origin', self.branch_name], 
            cwd=self.directory, check=True)
      print(f"Pushed branch {self.branch_name} to remote")
      return True
      
    except subprocess.CalledProcessError as e:
      print(f"Error pushing branch: {e}")
      # Try to get more details about the error
      try:
        result = subprocess.run(['git', 'remote', '-v'], cwd=self.directory, 
                  capture_output=True, text=True)
        print(f"Remote repositories: {result.stdout}")
      except:
        pass
      return False
  
  def _verify_changes(self) -> bool:
    """Verify that actual changes were made to files."""
    try:
      # Check if there are any changes in the working directory
      result = subprocess.run(['git', 'status', '--porcelain'], 
                cwd=self.directory, capture_output=True, text=True)
      
      print(f"Git status output: {result.stdout}")
      
      if not result.stdout.strip():
        print("No changes detected in git status")
        return False
      
      # Check if there are actual file modifications
      modified_files = []
      for line in result.stdout.strip().split('\n'):
        print(f"Git status line: {line}")
        if line.startswith('M ') or line.startswith(' A'):  # Modified or added files
          modified_files.append(line[2:].strip())
      
      print(f"Modified files found: {len(modified_files)}")
      return len(modified_files) > 0
      
    except Exception as e:
      print(f"Error verifying changes: {e}")
      return False
  
  def create_pull_request(self, title: str = None, description: str = None) -> bool:
    """Create a pull request on GitHub."""
    if not self.github_token:
      print("GitHub token not provided. Set GITHUB_TOKEN environment variable or use --github-token option.")
      print("Skipping PR creation.")
      return False
      
    if not self.repo_owner or not self.repo_name:
      print("GitHub repository information not available. Could not detect from git remote.")
      print("Please provide --repo-owner and --repo-name options.")
      print("Skipping PR creation.")
      return False
    
    if not title:
      title = f"Text replacement: {len(self.changes_made)} files modified"
    
    if not description:
      description = f"""## Text Replacement Summary

This PR contains automated text replacements across {len(self.changes_made)} files.

### Files Modified:
"""
      for change in self.changes_made:
        description += f"- {change['file']} ({change['replacements']} replacements)\n"
    
    url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls"
    headers = {
      "Authorization": f"token {self.github_token}",
      "Accept": "application/vnd.github.v3+json"
    }
    # Get the base branch (the branch we're branching from)
    base_branch = self._get_current_branch()
    
    data = {
      "title": title,
      "body": description,
      "head": self.branch_name,
      "base": base_branch
    }
    
    try:
      response = requests.post(url, headers=headers, json=data)
      response.raise_for_status()
      
      pr_data = response.json()
      print(f"Created PR: {pr_data['html_url']}")
      return True
      
    except requests.RequestException as e:
      print(f"Error creating PR: {e}")
      return False
  
  def run_full_workflow(self, search_pattern: str, replacement: str, 
            file_extensions: List[str] = None, use_regex: bool = False,
            branch_name: str = None, commit_message: str = None,
            pr_title: str = None, pr_description: str = None,
            max_files: int = 10000, exclude_dirs: List[str] = None) -> bool:
    """Run the complete workflow: replace text, create branch, commit, push, and create PR."""
    
    print("🚀 Starting Text Replacement Workflow")
    print("=" * 50)
    
    # Validate directory
    if not self.validate_directory():
      return False
    
    # Create branch
    if not self.create_branch(branch_name, interactive=False):
      return False
    
    # Replace text
    result = self.replace_text(search_pattern, replacement, file_extensions, use_regex, max_files, exclude_dirs, dry_run=False)
    
    if result["files_changed"] == 0:
      print("No changes were made. Exiting workflow.")
      # Switch back to original branch if no changes
      try:
        subprocess.run(['git', 'checkout', '-'], cwd=self.directory, check=True)
        print("Switched back to original branch.")
      except:
        pass
      return False
    
    # Verify changes were made
    if not self._verify_changes():
      print("No actual changes detected. Exiting workflow.")
      # Switch back to original branch
      try:
        subprocess.run(['git', 'checkout', '-'], cwd=self.directory, check=True)
        print("Switched back to original branch.")
      except:
        pass
      return False
    
    # Commit changes
    if not self.commit_changes(commit_message):
      return False
    
    # Push branch
    if not self.push_branch():
      return False
    
    # Create PR
    if not self.create_pull_request(pr_title, pr_description):
      print("PR creation failed, but changes have been pushed to the branch.")
      return False
    
    print("=" * 50)
    print("✅ Workflow completed successfully!")
    return True


def main():
  """Simple CLI interface for the Text Replacer tool."""
  parser = argparse.ArgumentParser(description="Text Replacer Tool - Use web UI for better experience")
  parser.add_argument("directory", help="Directory to search in")
  parser.add_argument("search", help="Text to search for")
  parser.add_argument("replace", help="Text to replace with")
  parser.add_argument("--dry-run", action="store_true", help="Preview changes without making them")
  parser.add_argument("--max-files", type=int, default=10000, help="Maximum number of files to process")
  
  args = parser.parse_args()
  
  # Initialize replacer
  replacer = TextReplacer(directory=args.directory)
  
  if args.dry_run:
    print("🔍 Running dry run...")
    result = replacer.replace_text(
      search_text=args.search,
      replace_text=args.replace,
      max_files=args.max_files,
      dry_run=True
    )
    print(f"📊 Files processed: {result['files_processed']}, Files changed: {result['files_changed']}")
  else:
    print("🚀 Starting replacement...")
    result = replacer.replace_text(
      search_text=args.search,
      replace_text=args.replace,
      max_files=args.max_files
    )
    print(f"✅ Replacement completed: {result['files_changed']} files changed")
  
  print("\n💡 For advanced features, use the web UI: python app.py")


if __name__ == "__main__":
  main()
