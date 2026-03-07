#!/bin/bash
# skill-validator 경로 설정
VALIDATOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WORK_DIR="$VALIDATOR_DIR/work"
export LOG="$VALIDATOR_DIR/debate-log.md"
