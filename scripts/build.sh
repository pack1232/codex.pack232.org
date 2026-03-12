#!/bin/bash
set -euo pipefail

# Build the Astro/Starlight site
cd "$(dirname "$0")/../sites/justonehourperweek"
pnpm build
