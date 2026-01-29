# Git Cheatsheet

## Daily Commands
```bash
git status                    # Check what's changed
git add <file>                # Stage file
git add .                     # Stage all
git commit -m "message"       # Commit
git push                      # Push to fork
git pull                      # Pull from fork
```

## Sync from Upstream
```bash
git fetch upstream
git merge upstream/main
git push
```

## Branches
```bash
git checkout -b feature-name  # Create branch
git checkout main             # Switch to main
git merge feature-name        # Merge branch
git branch -d feature-name    # Delete branch
```

## Undo
```bash
git reset HEAD <file>         # Unstage file
git checkout -- <file>        # Discard changes
git reset --soft HEAD~1       # Undo last commit (keep changes)
```

## Setup (one-time)
```bash
git remote add upstream https://github.com/frdel/agent-zero.git
```
