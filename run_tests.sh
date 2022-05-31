#!/usr/bin/env bash

set -e

clean_up_env() {
  rm -f integration-test.sqlite3
}

clean_up_env

# run test
python -m pytest

clean_up_env
