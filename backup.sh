#!/bin/bash
# Agent Zero Local Backup Script
# Creates timestamped backup archives of critical data

set -e

# Configuration
BACKUP_DIR="/a0/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_NAME="backup_${TIMESTAMP}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Critical directories and files to backup
BACKUP_TARGETS=(
    "memory"
    "knowledge"
    "prompts"
    "instruments"
    "mcp_servers"
    "tmp/settings.json"
    ".env"
)

echo "========================================"
echo "Agent Zero Backup Script"
echo "========================================"
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Create backup directory if missing
mkdir -p "${BACKUP_DIR}"

# Build list of existing targets
EXISTING_TARGETS=()
echo "Checking backup targets..."
for target in "${BACKUP_TARGETS[@]}"; do
    if [ -e "/a0/${target}" ]; then
        echo "  ✓ ${target}"
        EXISTING_TARGETS+=("${target}")
    else
        echo "  ✗ ${target} (skipped - not found)"
    fi
done
echo ""

# Check if anything to backup
if [ ${#EXISTING_TARGETS[@]} -eq 0 ]; then
    echo "ERROR: No backup targets found!"
    exit 1
fi

# Create backup archive
echo "Creating backup archive..."
cd /a0
tar -czf "${BACKUP_PATH}" "${EXISTING_TARGETS[@]}" 2>/dev/null

# Report results
BACKUP_SIZE=$(ls -lh "${BACKUP_PATH}" | awk '{print $5}')
echo ""
echo "========================================"
echo "Backup Complete!"
echo "========================================"
echo "Location: ${BACKUP_PATH}"
echo "Size: ${BACKUP_SIZE}"
echo "Contents: ${#EXISTING_TARGETS[@]} items backed up"
echo ""
