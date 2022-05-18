#!/usr/bin/env bash

set -e
export GET_YOUR_VPN_CONFIG_PATH=tests/test_config.ini
python -m pytest
