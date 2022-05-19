#!/usr/bin/env bash

set -e

clean_up_env() {
  rm integration-test.sqlite3
}

clean_up_env
export GET_YOUR_VPN_CONFIG_PATH=tests/test_config.ini

# run test
python -m pytest

clean_up_env
