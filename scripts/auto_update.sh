
### `auto_update.sh`
```bash
#!/bin/bash
# Update local branch with remote changes and push local commits.
# Usage: ./auto_update.sh

set -e

branch=$(git rev-parse --abbrev-ref HEAD)

echo "Pulling latest changes from origin/$branch"
git pull --rebase origin "$branch"

echo "Pushing local commits"
git push origin "$branch"
