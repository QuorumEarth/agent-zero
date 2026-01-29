# Backup Guide: Agent Zero Data

## What to Backup
| Folder/File | Contains |
|-------------|----------|
| `memory/` | Agent memories |
| `knowledge/` | Knowledge bases |
| `prompts/` | Custom prompts/agents |
| `instruments/` | Custom instruments |
| `tmp/mcp/` | MCP configs |
| `tmp/settings.json` | Settings |
| `.env` | API keys |

## Create Backup
```bash
# From /a0 directory
BACKUP_DIR=~/a0-backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

cp -r memory knowledge prompts instruments "$BACKUP_DIR/"
cp -r tmp/mcp "$BACKUP_DIR/"
cp tmp/settings.json .env "$BACKUP_DIR/" 2>/dev/null

echo "Backup saved to: $BACKUP_DIR"
```

## Restore from Backup
```bash
# Replace BACKUP_DIR with your backup path
BACKUP_DIR=~/a0-backups/20250129-120000

cp -r "$BACKUP_DIR/memory" "$BACKUP_DIR/knowledge" "$BACKUP_DIR/prompts" "$BACKUP_DIR/instruments" .
cp -r "$BACKUP_DIR/mcp" tmp/
cp "$BACKUP_DIR/settings.json" tmp/
cp "$BACKUP_DIR/.env" .
```

## List Backups
```bash
ls -la ~/a0-backups/
```
