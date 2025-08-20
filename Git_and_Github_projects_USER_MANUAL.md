# USER MANUAL - PCEP Rapid Practice System

## How to Fork a Repository on GitHub

### Prerequisites
- A GitHub account
- Web browser
- Internet connection

### Step-by-Step Instructions

#### Step 1: Navigate to the Repository
1. **Open your web browser** and go to GitHub.com
2. **Navigate to the repository** you want to fork by:
   - Using the direct URL (e.g., `https://github.com/owner/repository-name`)
   - Searching for the repository using GitHub's search bar
   - Following a link from an invitation email

#### Step 2: Locate the Fork Button
1. **Look at the top-right area** of the repository page
2. **Find the "Fork" button** - it's located near the top-right corner, usually next to "Star" and "Watch" buttons
3. The button will display the current number of forks (e.g., "Fork 25")

#### Step 3: Click the Fork Button
1. **Click the "Fork" button**
2. If you belong to multiple organizations, GitHub will show you a list of accounts where you can create the fork

#### Step 4: Choose Fork Destination
1. **Select your personal account** (or organization) as the destination for the fork
2. **Optionally modify the repository name** if you want to rename it
3. **Add a description** (optional) to explain your fork's purpose
4. **Choose whether to fork all branches** or just the main branch
   - For most cases, forking only the main branch is sufficient
   - Check "Copy the main branch only" for a lighter fork

#### Step 5: Create the Fork
1. **Click "Create fork"** button
2. **Wait for GitHub to process** - this usually takes a few seconds
3. GitHub will redirect you to your new forked repository

#### Step 6: Verify the Fork
1. **Check the repository URL** - it should now show your username: `https://github.com/YOUR-USERNAME/repository-name`
2. **Look for the fork indicator** - you'll see "forked from original-owner/repository-name" below the repository name
3. **Verify the fork relationship** - the original repository link will be displayed

### What Happens When You Fork?

- **Creates a copy**: You get a complete copy of the repository under your account
- **Independent development**: You can make changes without affecting the original
- **Maintains connection**: GitHub tracks the relationship between your fork and the original
- **Enables collaboration**: You can submit pull requests back to the original repository

### Next Steps After Forking

#### Option 1: Work Directly on GitHub
- Edit files directly in the GitHub web interface
- Make commits through the web editor
- Create branches and manage your fork online

#### Option 2: Clone to Your Local Machine
1. **Copy the clone URL** from your fork (green "Code" button)
2. **Open your terminal/command prompt**
3. **Run the clone command**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/repository-name.git
   cd repository-name
   ```
4. **Set up upstream remote** to track the original repository:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/repository-name.git
   git remote -v
   ```

### Managing Your Fork

#### Keeping Your Fork Updated
```bash
# Fetch updates from the original repository
git fetch upstream

# Switch to your main branch
git checkout main

# Merge updates from upstream
git merge upstream/main

# Push updates to your fork
git push origin main
```

#### Creating Feature Branches
```bash
# Create a new branch for your changes
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "Add your feature description"

# Push the branch to your fork
git push origin feature/your-feature-name
```

#### Submitting Pull Requests
1. **Go to your fork on GitHub**
2. **Click "Compare & pull request"** (appears after pushing a branch)
3. **Fill out the pull request form**:
   - Add a descriptive title
   - Explain what changes you made
   - Reference any relevant issues
4. **Submit the pull request** to the original repository

### Common Fork Scenarios

#### Scenario 1: Contributing to Open Source
- Fork the project
- Create a feature branch
- Make your improvements
- Submit a pull request

#### Scenario 2: Personal Customization
- Fork to create your own version
- Modify for your specific needs
- Keep as a private fork or share with others

#### Scenario 3: Learning and Experimentation
- Fork to safely experiment with code
- Try new features without risk
- Learn from existing codebases

### Troubleshooting

#### Problem: Can't See Fork Button
- **Check if you're logged in** to GitHub
- **Verify repository permissions** - some private repos can't be forked
- **Refresh the page** and try again

#### Problem: Fork Failed
- **Check your account limits** - free accounts have repository limits
- **Verify the repository isn't too large**
- **Try again after a few minutes**

#### Problem: Fork Doesn't Update
- Forks don't automatically sync with the original
- **Manually pull updates** using the upstream remote
- Use GitHub's "Sync fork" button on the web interface

### Best Practices

1. **Fork with purpose** - have a clear reason for forking
2. **Keep forks updated** - regularly sync with the upstream repository  
3. **Use descriptive branch names** - make it clear what each branch does
4. **Write clear commit messages** - explain what and why you changed
5. **Submit focused pull requests** - one feature or fix per PR
6. **Follow the project's contribution guidelines** - read CONTRIBUTING.md if available

### Security Considerations

- **Review code before forking** - especially for sensitive projects
- **Be cautious with credentials** - don't commit secrets or API keys
- **Understand license implications** - respect the original project's license
- **Keep forks private if needed** - for proprietary or sensitive work

## How to Commit a New Local Repository from VS Code to GitHub

### Prerequisites
- VS Code installed with Git support
- A GitHub account
- Git installed on your local machine
- Internet connection

### Step-by-Step Instructions

#### Step 1: Initialize Git Repository in VS Code
1. **Open your project folder** in VS Code
2. **Open the integrated terminal** (`Ctrl+`` ` or `View > Terminal`)
3. **Initialize Git repository**:
   ```bash
   git init
   ```
4. **Verify initialization** - you should see a `.git` folder created (may be hidden)

#### Step 2: Configure Git (If First Time)
If you haven't configured Git on your machine yet:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Step 3: Stage Your Files
1. **Open Source Control panel** in VS Code (`Ctrl+Shift+G`)
2. **Review your files** - all files will appear under "Changes"
3. **Stage files** by either:
   - **Option A**: Click the `+` button next to each file to stage individually
   - **Option B**: Click the `+` button next to "Changes" to stage all files
   - **Option C**: Use terminal command:
     ```bash
     git add .
     ```

#### Step 4: Create Your First Commit
1. **In Source Control panel**, enter a commit message in the text box
2. **Use a descriptive message** like "Initial commit" or "Add project files"
3. **Commit your changes** by either:
   - **Option A**: Click the checkmark (✓) button
   - **Option B**: Use `Ctrl+Enter`
   - **Option C**: Use terminal command:
     ```bash
     git commit -m "Initial commit"
     ```

#### Step 5: Create Repository on GitHub
1. **Go to GitHub.com** and sign in to your account
2. **Click the "+" icon** in the top-right corner
3. **Select "New repository"**
4. **Fill out repository details**:
   - **Repository name**: Choose a meaningful name
   - **Description**: Optional but recommended
   - **Visibility**: Choose Public or Private
   - **DON'T initialize** with README, .gitignore, or license (since you already have local files)
5. **Click "Create repository"**

#### Step 6: Connect Local Repository to GitHub
1. **Copy the repository URL** from GitHub (HTTPS or SSH)
2. **In VS Code terminal**, add the remote origin:
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git
   ```
3. **Verify remote connection**:
   ```bash
   git remote -v
   ```

#### Step 7: Push Your Code to GitHub
1. **Push your commits** to the main branch:
   ```bash
   git branch -M main
   git push -u origin main
   ```
2. **Enter GitHub credentials** if prompted
3. **Wait for upload** to complete

#### Step 8: Verify Upload
1. **Refresh your GitHub repository page**
2. **Verify all files** are now visible on GitHub
3. **Check commit history** to confirm your initial commit appears

### Using VS Code's Built-in GitHub Integration

#### Alternative Method: Publish to GitHub Directly
1. **Open Command Palette** (`Ctrl+Shift+P`)
2. **Type and select** "Git: Publish to GitHub"
3. **Choose repository visibility** (Public/Private)
4. **Enter repository name**
5. **VS Code will create the repository** and push your code automatically

#### Using GitHub Extension
1. **Install GitHub Pull Requests and Issues** extension
2. **Sign in to GitHub** through the extension
3. **Use integrated features** for easier repository management

### Making Future Commits

#### Regular Workflow
1. **Make changes** to your files
2. **Stage changes** in Source Control panel or use `git add .`
3. **Write commit message** describing your changes
4. **Commit changes** using checkmark button or `Ctrl+Enter`
5. **Push to GitHub**:
   ```bash
   git push
   ```

#### VS Code Source Control Features
- **View changes**: See diff of modified files
- **Commit history**: View previous commits using GitLens extension
- **Branch management**: Create and switch branches
- **Merge conflicts**: Resolve conflicts with visual editor

### Branch Management from VS Code

#### Creating New Branches
1. **Click branch name** in status bar (bottom-left)
2. **Select "Create new branch"**
3. **Enter branch name** and press Enter
4. **Push new branch**:
   ```bash
   git push -u origin BRANCH-NAME
   ```

#### Switching Branches
1. **Click branch name** in status bar
2. **Select desired branch** from the list
3. **VS Code switches** to selected branch

### Troubleshooting

#### Problem: Authentication Failed
- **Use Personal Access Token** instead of password
- **Generate token** in GitHub Settings > Developer settings > Personal access tokens
- **Use token as password** when prompted

#### Problem: Permission Denied
- **Check repository ownership** - ensure you have write access
- **Verify remote URL** - make sure it points to your repository
- **Check SSH keys** if using SSH authentication

#### Problem: Merge Conflicts
- **VS Code will highlight** conflicting areas
- **Choose which changes** to keep using the inline options
- **Commit resolved conflicts** after fixing

#### Problem: Large Files
- **Check file sizes** - GitHub has limits (100MB per file)
- **Use .gitignore** to exclude unnecessary files
- **Consider Git LFS** for large binary files

### Best Practices

1. **Write clear commit messages** - explain what and why you changed
2. **Commit frequently** - small, focused commits are easier to manage
3. **Use .gitignore** - exclude temporary files, logs, and sensitive data
4. **Keep commits atomic** - one logical change per commit
5. **Pull before pushing** - sync with remote changes first
6. **Use meaningful branch names** - describe the feature or fix

### Security Considerations

- **Never commit secrets** - API keys, passwords, or credentials
- **Use environment variables** - for configuration and sensitive data
- **Review .gitignore** - ensure sensitive files are excluded
- **Use private repositories** - for proprietary or sensitive code
- **Enable two-factor authentication** - on your GitHub account

### Common Git Commands Reference

```bash
# Check repository status
git status

# View commit history
git log --oneline

# Check which remote repositories are configured
git remote -v

# Pull latest changes from GitHub
git pull

# Push changes to GitHub
git push

# Create and switch to new branch
git checkout -b feature-branch-name

# Switch between branches
git checkout branch-name

# Merge branch into current branch
git merge branch-name

# View differences in files
git diff
```

---

*This guide covers the essential steps for forking repositories on GitHub. For more advanced Git and GitHub features, consult the official GitHub documentation.*