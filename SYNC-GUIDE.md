# Sync Guide: Upstream → Fork

## Quick Sync
```bash
git fetch upstream
git checkout quorum
git merge upstream/main
git push
```

## Check for Updates First
```bash
git fetch upstream
git log quorum..upstream/main --oneline  # Shows new commits
```

## If Conflicts Occur
```bash
# After merge shows CONFLICT:
git status                    # See conflicted files
# Edit files, remove <<<< ==== >>>> markers
git add <resolved-file>
git commit                    # Completes merge
git push
```

## Abort Failed Merge
```bash
git merge --abort             # Back to pre-merge state
```

## Setup (one-time)
```bash
git remote add upstream https://github.com/frdel/agent-zero.git
```
