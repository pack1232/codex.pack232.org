#!/bin/bash
set -euo pipefail

# Build both Astro/Starlight sites
cd "$(dirname "$0")/.."

echo "Building justonehourperweek.com..."
pnpm --filter '@justonehourperweek/site' build

echo ""
echo "Building askyourspl.com..."
pnpm --filter '@askyourspl/site' build

echo ""
echo "Both sites built successfully."
