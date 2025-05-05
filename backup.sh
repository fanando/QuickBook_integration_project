#!/bin/bash
mkdir -p /backups
while true; do
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  pg_dump -h postgres -U postgres -d qbo > /backups/backup_$TIMESTAMP.sql
  echo "Backup saved: backup_$TIMESTAMP.sql"
  sleep 3600
done