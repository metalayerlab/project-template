#!/usr/bin/env bash
# Lint the Markdown and scan for secrets: what CI's Wiki standard and Secret
# scan jobs run, with the same images and arguments (they call this script).
# Template-owned. Without Docker it skips locally, but is an error in CI.
#
#   scripts/check-docs-secrets.sh            # both
#   scripts/check-docs-secrets.sh docs       # markdownlint-cli2 only
#   scripts/check-docs-secrets.sh secrets    # gitleaks only
set -euo pipefail
cd "$(dirname "$0")/.."

checks="${1:-docs secrets}"

if ! command -v docker > /dev/null 2>&1; then
    if [ "${CI:-}" = "true" ]; then
        echo "error: docker is not installed"
        exit 1
    fi
    echo "skip: docker is not installed"
    exit 0
fi

status=0
for check in $checks; do
    case "$check" in
        docs)
            # Config: .markdownlint-cli2.yaml (CHANGELOG.md is release-please's).
            echo "+ markdownlint-cli2"
            docker run --rm -v "$PWD:/workdir" davidanson/markdownlint-cli2:v0.24.0 \
                "docs/wiki/*.md" "*.md" "!CHANGELOG.md" || status=1
            ;;
        secrets)
            # Scans commits, as CI does. Allow-list false positives in .gitleaks.toml.
            echo "+ gitleaks"
            docker run --rm -v "$PWD:/repo" -w /repo ghcr.io/gitleaks/gitleaks:v8.30.1 \
                git --redact --verbose --config .gitleaks.toml . || status=1
            ;;
        *)
            echo "usage: $0 [docs|secrets]"
            exit 2
            ;;
    esac
done
exit "$status"
