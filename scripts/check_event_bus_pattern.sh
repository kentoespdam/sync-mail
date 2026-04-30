#!/usr/bin/env bash
# scripts/check_event_bus_pattern.sh
# Prevents the incorrect event_bus.Event(...) pattern from being committed.

set -e

# Search for the pattern in staged files
# We only care about .py files in src/
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | grep '^src/' || true)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

if grep -E "event_bus\s*\.\s*Event" $STAGED_FILES; then
    echo "ERROR: Incorrect event bus usage pattern detected!"
    echo "Use 'Event(...)' instead of 'event_bus.Event(...)'."
    echo "Ensure 'Event' is imported from 'sync_mail.observability'."
    exit 1
fi

exit 0
