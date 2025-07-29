# Git and GitHub Complete User Guide: Safe and Secure Version Control

**Document Version**: 1.1  
**Date**: July 29, 2025  
**Purpose**: Comprehensive guide for using Git and GitHub.com for version control  
**Audience**: Developers at all levels seeking safe and secure version control practices  
**Updated**: Added section on renaming default branch from master to main

---

## Table of Contents

1. [Overview and Benefits](#overview-and-benefits)
2. [Initial Setup and Configuration](#initial-setup-and-configuration)
3. [Renaming Default Branch from Master to Main](#renaming-default-branch-from-master-to-main)
4. [Top 10 Most Used Git Commands](#top-10-most-used-git-commands)
5. [Creating Repositories](#creating-repositories)
6. [Basic Workflow](#basic-workflow)
7. [Branching and Merging](#branching-and-merging)
8. [Remote Repository Management](#remote-repository-management)
9. [Security Best Practices](#security-best-practices)
10. [Common Scenarios and Solutions](#common-scenarios-and-solutions)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Advanced Tips and Best Practices](#advanced-tips-and-best-practices)

---

## Overview and Benefits

### What is Git?
Git is a distributed version control system that tracks changes in files and coordinates work among multiple people. It provides:

- **Version History**: Complete history of all changes
- **Branching**: Work on features independently
- **Collaboration**: Multiple developers can work on the same project
- **Backup**: Distributed nature provides automatic backups
- **Rollback**: Easy to revert to previous versions

### What is GitHub?
GitHub is a cloud-based hosting service for Git repositories that adds:

- **Remote Storage**: Cloud backup of your repositories
- **Collaboration Tools**: Pull requests, issues, project management
- **Social Coding**: Share and discover projects
- **CI/CD Integration**: Automated testing and deployment
- **Security Features**: Vulnerability scanning, dependency management

---

## Initial Setup and Configuration

### 1. Install Git

#### Windows:
```bash
# Download from https://git-scm.com/download/win
# Or use package manager
winget install Git.Git
```

#### macOS:
```bash
# Using Homebrew
brew install git

# Or download from https://git-scm.com/download/mac
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install git
```

### 2. Global Configuration

```bash
# Set your identity (required)
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"

# Set default branch name (recommended for new repositories)
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "code --wait"  # VS Code
# git config --global core.editor "nano"       # Nano
# git config --global core.editor "vim"        # Vim

# Improve command output
git config --global color.ui auto

# Set line ending handling (important for cross-platform)
# Windows:
git config --global core.autocrlf true
# macOS/Linux:
git config --global core.autocrlf input

# Verify configuration
git config --list
```

### 3. GitHub Account Setup

1. **Create Account**: Visit [github.com](https://github.com) and sign up
2. **Enable Two-Factor Authentication**: Settings → Security → Two-factor authentication
3. **Set up SSH Keys** (recommended for security):

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
# Windows:
clip < ~/.ssh/id_ed25519.pub
# macOS:
pbcopy < ~/.ssh/id_ed25519.pub
# Linux:
cat ~/.ssh/id_ed25519.pub
```

4. **Add SSH Key to GitHub**: Settings → SSH and GPG keys → New SSH key

---

## Renaming Default Branch from Master to Main

### Why Change from Master to Main?
Modern best practices recommend using `main` as the default branch name for inclusivity. GitHub now defaults to `main` for new repositories, and many organizations have adopted this standard.

### Method 1: For Existing Local Repository

```bash
# 1. Switch to the master branch (if not already there)
git checkout master

# 2. Rename the branch locally
git branch -m master main

# 3. Push the new main branch to remote
git push -u origin main

# 4. Update the default branch on GitHub
# Go to GitHub → Repository → Settings → Branches → Switch default branch to 'main'

# 5. Delete the old master branch from remote (after updating GitHub default)
git push origin --delete master
```

### Method 2: For New Repositories (Prevention)

```bash
# Set main as default for all new repositories globally
git config --global init.defaultBranch main

# Now when you create new repositories:
git init
# This will automatically create 'main' branch instead of 'master'
```

### Method 3: Complete Step-by-Step Process

```bash
# Step 1: Ensure you're on master branch
git status
git checkout master

# Step 2: Rename branch locally
git branch -m master main

# Step 3: Push new branch and set upstream
git push -u origin main

# Step 4: Update GitHub default branch (via web interface)
# - Go to your repository on GitHub
# - Click Settings tab
# - Click Branches in left sidebar
# - Click pencil icon next to default branch
# - Select 'main' from dropdown
# - Click Update

# Step 5: Update local tracking (if needed)
git branch --set-upstream-to=origin/main main

# Step 6: Delete old master branch from remote
git push origin --delete master

# Step 7: Clean up local references
git remote prune origin
```

### Method 4: GitHub CLI (if you have it installed)

```bash
# Rename branch locally
git branch -m master main
git push -u origin main

# Update default branch on GitHub using CLI
gh repo edit --default-branch main

# Delete old master branch
git push origin --delete master
```

### Important Considerations

1. **Team Coordination**: Notify team members before making this change
2. **CI/CD Updates**: Update any build scripts or CI/CD configurations that reference `master`
3. **Documentation**: Update README files and documentation that mention `master`
4. **Clone URLs**: Existing clone commands will still work, but new clones will use `main`

### For Team Members After the Change

```bash
# When team members pull the changes:
git checkout master
git pull origin main
git branch -m master main
git branch --set-upstream-to=origin/main main

# Or simply:
git fetch origin
git checkout main
git branch -d master  # delete local master branch
```

### Update Any Scripts or Aliases

If you have any scripts or Git aliases that reference `master`, update them:

```bash
# Example: Update alias that was pointing to master
git config --global alias.mainpull "pull origin master"
# Change to:
git config --global alias.mainpull "pull origin main"
```

---

## Top 10 Most Used Git Commands

### 1. `git status` - Check Repository Status
```bash
# Shows current branch, modified files, staged changes
git status

# Short format
git status -s
```

### 2. `git add` - Stage Changes
```bash
# Stage specific file
git add filename.txt

# Stage all changes in current directory
git add .

# Stage all changes in repository
git add -A

# Stage parts of a file interactively
git add -p filename.txt
```

### 3. `git commit` - Create Snapshots
```bash
# Commit with message
git commit -m "Add user authentication feature"

# Commit with detailed message
git commit -m "Add user authentication" -m "- Implement JWT tokens
- Add login/logout endpoints
- Add password hashing"

# Commit all tracked changes (skip staging)
git commit -am "Quick fix for login bug"

# Amend last commit
git commit --amend -m "Updated commit message"
```

### 4. `git push` - Upload to Remote
```bash
# Push to default remote and branch
git push

# Push to specific remote and branch
git push origin main

# Push new branch to remote
git push -u origin feature-branch

# Force push (use with caution)
git push --force-with-lease
```

### 5. `git pull` - Download from Remote
```bash
# Pull from default remote
git pull

# Pull from specific remote and branch
git pull origin main

# Pull with rebase (cleaner history)
git pull --rebase
```

### 6. `git clone` - Copy Repository
```bash
# Clone via HTTPS
git clone https://github.com/username/repository.git

# Clone via SSH (recommended)
git clone git@github.com:username/repository.git

# Clone to specific directory
git clone git@github.com:username/repository.git my-project

# Clone specific branch
git clone -b develop git@github.com:username/repository.git
```

### 7. `git branch` - Manage Branches
```bash
# List all branches
git branch

# List remote branches
git branch -r

# List all branches (local and remote)
git branch -a

# Create new branch
git branch feature-name

# Delete branch
git branch -d feature-name

# Delete branch forcefully
git branch -D feature-name
```

### 8. `git checkout` / `git switch` - Change Branches
```bash
# Switch to existing branch (older syntax)
git checkout main

# Switch to existing branch (newer syntax)
git switch main

# Create and switch to new branch
git checkout -b feature-name
git switch -c feature-name

# Switch to previous branch
git switch -
```

### 9. `git merge` - Combine Branches
```bash
# Merge feature branch into current branch
git merge feature-branch

# Merge with no fast-forward (creates merge commit)
git merge --no-ff feature-branch

# Abort merge if conflicts occur
git merge --abort
```

### 10. `git log` - View History
```bash
# View commit history
git log

# One line per commit
git log --oneline

# Show last 5 commits
git log -5

# Show commits with file changes
git log --stat

# Show commits graphically
git log --graph --oneline --all

# Show commits by specific author
git log --author="Your Name"
```

---

## Creating Repositories

### Method 1: Start with Local Repository

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize Git repository
git init

# Add files to staging
git add .

# Create initial commit
git commit -m "Initial commit"

# Create repository on GitHub (via web interface)
# Then connect local to remote:
git remote add origin git@github.com:username/repository.git
git branch -M main
git push -u origin main
```

### Method 2: Start with GitHub Repository

```bash
# Create repository on GitHub first (via web interface)
# Then clone locally:
git clone git@github.com:username/repository.git
cd repository

# Start working on your project
# Add files, commit, and push as needed
```

### Method 3: Fork an Existing Repository

```bash
# Fork repository via GitHub web interface
# Then clone your fork:
git clone git@github.com:yourusername/forked-repository.git
cd forked-repository

# Add original repository as upstream
git remote add upstream git@github.com:originalowner/repository.git

# Keep your fork updated
git fetch upstream
git checkout main
git merge upstream/main
```

---

## Basic Workflow

### Daily Git Workflow

```bash
# 1. Start your day - update your local repository
git pull origin main

# 2. Create a feature branch
git switch -c feature/user-login

# 3. Make changes to your files
# ... edit files ...

# 4. Check what changed
git status
git diff

# 5. Stage your changes
git add .

# 6. Commit your changes
git commit -m "Implement user login functionality"

# 7. Push your branch
git push -u origin feature/user-login

# 8. Create Pull Request via GitHub web interface

# 9. After PR is merged, clean up
git switch main
git pull origin main
git branch -d feature/user-login
```

### Commit Message Best Practices

```bash
# Good commit messages:
git commit -m "Add user authentication middleware"
git commit -m "Fix memory leak in image processing"
git commit -m "Update README with installation instructions"

# Format for detailed commits:
git commit -m "Summary of changes (50 chars or less)

More detailed explanation of what and why, not how.
Can include multiple paragraphs.

- Bullet points are okay
- Use present tense: 'Add feature' not 'Added feature'
- Reference issues: Fixes #123"
```

---

## Branching and Merging

### Branch Strategy - GitHub Flow

```bash
# Main branch is always deployable
# Create feature branches for new work

# 1. Create feature branch
git switch -c feature/payment-integration

# 2. Work on feature
git add .
git commit -m "Add payment API integration"

# 3. Push branch
git push -u origin feature/payment-integration

# 4. Create Pull Request on GitHub

# 5. After review and approval, merge via GitHub

# 6. Update local main branch
git switch main
git pull origin main

# 7. Delete feature branch
git branch -d feature/payment-integration
git push origin --delete feature/payment-integration
```

### Handling Merge Conflicts

```bash
# When merge conflicts occur:
git merge feature-branch
# Auto-merging file.txt
# CONFLICT (content): Merge conflict in file.txt
# Automatic merge failed; fix conflicts and then commit.

# 1. Check which files have conflicts
git status

# 2. Open conflicted files and resolve conflicts
# Look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> feature-branch

# 3. After resolving conflicts:
git add resolved-file.txt

# 4. Complete the merge
git commit -m "Resolve merge conflicts"
```

---

## Remote Repository Management

### Working with Remotes

```bash
# View remote repositories
git remote -v

# Add remote repository
git remote add origin git@github.com:username/repository.git
git remote add upstream git@github.com:upstream/repository.git

# Change remote URL
git remote set-url origin git@github.com:username/new-repository.git

# Remove remote
git remote remove upstream

# Fetch from remote (doesn't merge)
git fetch origin

# Fetch all remotes
git fetch --all

# Push to remote
git push origin main

# Set upstream tracking
git push -u origin feature-branch
```

### Syncing with Upstream (For Forks)

```bash
# Keep your fork updated with upstream changes
git fetch upstream
git switch main
git merge upstream/main
git push origin main

# Or use rebase for cleaner history
git fetch upstream
git switch main
git rebase upstream/main
git push origin main
```

---

## Security Best Practices

### 1. SSH Key Management

```bash
# Use SSH keys instead of HTTPS for better security
# Generate different keys for different purposes
ssh-keygen -t ed25519 -C "work-email@company.com" -f ~/.ssh/id_ed25519_work
ssh-keygen -t ed25519 -C "personal@email.com" -f ~/.ssh/id_ed25519_personal

# Configure SSH config file (~/.ssh/config)
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work

Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

# Use different remotes for different contexts
git remote add origin git@github-work:company/repository.git
```

### 2. Protect Sensitive Information

```bash
# Create .gitignore file to exclude sensitive files
echo "config/secrets.json" >> .gitignore
echo "*.env" >> .gitignore
echo "node_modules/" >> .gitignore
echo ".DS_Store" >> .gitignore

# If you accidentally committed sensitive data:
# 1. Change the sensitive data (passwords, keys, etc.)
# 2. Remove from Git history:
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch path/to/sensitive/file' \
--prune-empty --tag-name-filter cat -- --all

# 3. Force push (this rewrites history - use carefully)
git push origin --force --all
```

### 3. GPG Signing (Optional but Recommended)

```bash
# Generate GPG key
gpg --full-generate-key

# List GPG keys
gpg --list-secret-keys --keyid-format LONG

# Configure Git to use GPG key
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true

# Sign individual commits
git commit -S -m "Signed commit message"
```

### 4. Repository Security Settings

**On GitHub:**
1. **Branch Protection**: Settings → Branches → Add rule
   - Require pull request reviews
   - Require status checks
   - Include administrators
   - Restrict pushes

2. **Security Alerts**: Settings → Security & analysis
   - Enable dependency alerts
   - Enable automated security fixes

3. **Access Control**:
   - Use teams for organization repositories
   - Regularly audit collaborators
   - Use least privilege principle

---

## Common Scenarios and Solutions

### Scenario 1: Undo Last Commit (Not Pushed)

```bash
# Keep changes in working directory
git reset --soft HEAD~1

# Remove changes completely
git reset --hard HEAD~1

# Undo specific file from last commit
git reset HEAD~1 filename.txt
```

### Scenario 2: Undo Changes in Working Directory

```bash
# Discard changes in specific file
git checkout -- filename.txt

# Discard all changes
git checkout -- .

# Or using newer syntax
git restore filename.txt
git restore .
```

### Scenario 3: Fix Wrong Branch

```bash
# You committed to wrong branch
# 1. Create correct branch from current state
git branch correct-branch

# 2. Reset current branch to previous state
git reset --hard HEAD~1

# 3. Switch to correct branch
git switch correct-branch
```

### Scenario 4: Stash Work in Progress

```bash
# Save current work without committing
git stash

# Save with message
git stash save "Work in progress on login feature"

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply specific stash
git stash apply stash@{2}

# Apply and remove from stash list
git stash pop

# Drop specific stash
git stash drop stash@{1}
```

### Scenario 5: Cherry-pick Specific Commits

```bash
# Apply specific commit from another branch
git cherry-pick commit-hash

# Cherry-pick multiple commits
git cherry-pick commit1 commit2 commit3

# Cherry-pick a range of commits
git cherry-pick start-commit..end-commit
```

---

## Troubleshooting Guide

### Problem: "Permission denied (publickey)"

```bash
# Solution 1: Check SSH agent
ssh-add -l

# Solution 2: Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Solution 3: Test SSH connection
ssh -T git@github.com
```

### Problem: "Your branch is ahead of 'origin/main' by X commits"

```bash
# Solution: Push your commits
git push origin main

# Or if you want to discard local commits
git reset --hard origin/main
```

### Problem: "Please tell me who you are"

```bash
# Solution: Configure user identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Problem: Large File Issues

```bash
# GitHub has a 100MB file size limit
# Use Git LFS for large files

# Install Git LFS
git lfs install

# Track large files
git lfs track "*.zip"
git lfs track "*.mp4"

# Add .gitattributes file
git add .gitattributes

# Normal git workflow for LFS files
git add large-file.zip
git commit -m "Add large file"
git push origin main
```

### Problem: Merge Conflicts

```bash
# When conflicts occur during merge/pull:
# 1. Check conflicted files
git status

# 2. Open files and resolve conflicts manually
# Or use merge tool
git mergetool

# 3. After resolving conflicts
git add resolved-files
git commit

# 4. Continue with merge
git merge --continue
```

---

## Advanced Tips and Best Practices

### 1. Useful Git Aliases

```bash
# Set up helpful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'

# Advanced aliases
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
git config --global alias.adog "log --all --decorate --oneline --graph"
```

### 2. Interactive Rebase (Rewrite History)

```bash
# Rewrite last 3 commits
git rebase -i HEAD~3

# In the editor, you can:
# pick = use commit
# reword = use commit, but edit message
# edit = use commit, but stop for amending
# squash = use commit, but meld into previous commit
# fixup = like squash, but discard commit message
# drop = remove commit
```

### 3. Git Hooks

```bash
# Pre-commit hook example (.git/hooks/pre-commit)
#!/bin/sh
# Run tests before allowing commit
npm test
if [ $? -ne 0 ]; then
    echo "Tests must pass before commit!"
    exit 1
fi
```

### 4. Search and Blame

```bash
# Search for text in commit messages
git log --grep="bug fix"

# Search for code changes
git log -S "function_name"

# Show who last modified each line
git blame filename.txt

# Show changes in specific function
git log -L :function_name:filename.py
```

### 5. Maintenance Commands

```bash
# Clean up merged branches
git branch --merged | grep -v "\*\|main\|master" | xargs -n 1 git branch -d

# Garbage collection (cleanup)
git gc

# Check repository integrity
git fsck

# Show repository size
git count-objects -vH

# Clean untracked files
git clean -fd

# Prune remote tracking branches
git remote prune origin
```

---

## Quick Reference Card

### Essential Commands Summary

| Command | Description | Example |
|---------|-------------|---------|
| `git init` | Initialize repository | `git init` |
| `git clone` | Copy repository | `git clone <url>` |
| `git status` | Check status | `git status` |
| `git add` | Stage changes | `git add .` |
| `git commit` | Create snapshot | `git commit -m "message"` |
| `git push` | Upload changes | `git push origin main` |
| `git pull` | Download changes | `git pull` |
| `git branch` | Manage branches | `git branch feature` |
| `git switch` | Change branches | `git switch main` |
| `git merge` | Combine branches | `git merge feature` |

### File States in Git

```
Untracked → Staged → Committed → Pushed
     ↓         ↓         ↓         ↓
 git add → git commit → git push
```

### Branch Flow

```
main ←── feature-branch
 ↓              ↑
pull         merge/PR
```

---

## Conclusion

Git and GitHub provide powerful version control capabilities that enable safe, secure, and collaborative software development. Key takeaways:

### Best Practices Summary:
1. **Commit often** with meaningful messages
2. **Use branches** for features and experiments
3. **Keep main branch stable** and deployable
4. **Review code** through pull requests
5. **Secure your account** with 2FA and SSH keys
6. **Back up regularly** by pushing to remote
7. **Learn gradually** - start with basics, add advanced features over time

### Daily Workflow Checklist:
- [ ] Pull latest changes: `git pull`
- [ ] Create feature branch: `git switch -c feature-name`
- [ ] Make changes and test
- [ ] Stage changes: `git add .`
- [ ] Commit: `git commit -m "description"`
- [ ] Push: `git push -u origin feature-name`
- [ ] Create pull request on GitHub
- [ ] After merge, clean up local branches

### Security Checklist:
- [ ] Use SSH keys for authentication
- [ ] Enable two-factor authentication on GitHub
- [ ] Never commit secrets or sensitive data
- [ ] Use .gitignore to exclude sensitive files
- [ ] Regularly update and rotate SSH keys
- [ ] Review repository access permissions

Remember: Git has a learning curve, but mastering these fundamentals will make you a more effective and confident developer. Practice these commands regularly, and don't be afraid to experiment in test repositories!

---

**Document Maintenance:**  
This guide should be updated as Git and GitHub evolve. Regular review of best practices and new features is recommended.

**Last Updated**: July 29, 2025  
**Next Review**: October 29, 2025

---

## Additional Resources

- **Official Git Documentation**: https://git-scm.com/doc
- **GitHub Documentation**: https://docs.github.com
- **Interactive Git Tutorial**: https://learngitbranching.js.org
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **Pro Git Book** (Free): https://git-scm.com/book
