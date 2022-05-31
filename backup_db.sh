#!/usr/bin/env bash

set -e

read_db_file_path() {
  awk -F "=" '/FilePath/ {print $2}' config.ini
}

backup_db() {
  echo "backup '$1' to '$1.backup'"
  sqlite3 $1 ".backup $1.backup"
}

_FILE=$(read_db_file_path)
backup_db $_FILE