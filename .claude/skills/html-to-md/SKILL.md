---
name: html-to-md
description: Convert a web page (HTML) to clean .md Markdown by extracting the primary body content. Use when the user wants to convert a web page to markdown format.
allowed-tools: Bash, Read, Write, Glob, WebFetch
argument-hint: [URL] [--source URL]
---

# Convert Web Page to Markdown

Convert the specified web page URL to a clean Markdown (.md) file with YAML frontmatter. Extracts only the primary body content, ignoring navigation, sidebars, footers, ads, and other chrome.

## Input

Parse `$ARGUMENTS` for:
- **URL** - the web page to convert (required). Must start with `http://` or `https://`.
- **--source URL** - optional. When provided, this URL is recorded in the `source` frontmatter field. This is set by the `doc-convert-to-markdown` parent skill. If not provided, the input URL itself is used as the source.

## Conversion Steps

1. **Fetch the page** - Use the `WebFetch` tool to retrieve the page content. Use the prompt: `"Extract the complete main body content of this page as clean text. Ignore navigation menus, headers, footers, sidebars, ads, cookie banners, and other non-content elements. Preserve all headings, lists, links, tables, and text formatting. Return the full content, not a summary."`

2. **Handle fetch failures** - If the page cannot be fetched or returns no usable content:
   - Inform the user that the page content could not be extracted.
   - Suggest using `--ref` mode to create a reference-only file instead.
   - Do NOT create an empty or near-empty .md file.

3. **Clean up the output** - The fetched content may need fixing:
   - Ensure proper heading hierarchy (promote the first meaningful heading to `#` if appropriate)
   - Convert any remaining HTML tags to markdown equivalents
   - Remove duplicate or boilerplate text that slipped through (e.g., "Skip to content", breadcrumbs)
   - Collapse excessive blank lines (3+ consecutive → 2)
   - Remove trailing whitespace from lines
   - Preserve links in `[text](url)` format
   - Preserve tables and list formatting

4. **Generate frontmatter** - Add YAML frontmatter to the top of the file following the rules below.

5. **Determine output path and filename** - Derive a filename from the URL path:
   - Use the last meaningful path segment (e.g., `bsa-scouter-code-of-conduct` from `.../gss/bsa-scouter-code-of-conduct/`)
   - Convert to a clean filename with `.md` extension (e.g., `bsa-scouter-code-of-conduct.md`)
   - Save to the same directory context as provided by the parent skill, or to `docs/tmp/` if invoked directly

6. **Write the output** - Save the cleaned markdown (with frontmatter) to the output path.

7. **Show the user the result** - Display the output file path and a brief summary of the content (first heading or first few lines).

## Frontmatter Specification

Every generated markdown file MUST begin with a YAML frontmatter block. Generate the following fields:

```yaml
---
title: ""          # Auto-detected (see rules below)
description: ""    # Brief 1-2 sentence summary of the page content
source_file: ""    # The URL slug or page identifier (e.g., "bsa-scouter-code-of-conduct")
converted_date: "" # Today's date in YYYY-MM-DD format
original_format: "html"
author: ""         # From page content if available, otherwise "Unknown"
tags: []           # 2-5 relevant lowercase tags derived from the content
category: ""       # Immediate parent directory name of the output file
draft: false
source: ""         # Optional: only include if --source was provided or if converting from a URL. Contains the page URL.
last_downloaded: "" # Optional: only include if --source was provided. Today's date in YYYY-MM-DD format.
---
```

### Auto-Detection Rules

- **title**: Use the first `#` heading in the extracted content. If none, derive from the URL path slug (e.g., `bsa-scouter-code-of-conduct` → `BSA Scouter Code of Conduct`). When the title comes from a `#` heading in the body, REMOVE that heading from the body to avoid duplication.
- **description**: Generate a concise 1-2 sentence summary of the page's purpose and content.
- **author**: Look for author attribution in the content. For organizational pages (e.g., scouting.org), use the organization name (e.g., `"Scouting America"`). Use `"Unknown"` if not determinable.
- **tags**: Analyze the content and assign 2-5 descriptive lowercase tags focused on subject matter.
- **category**: Use the immediate parent directory name of the output file.
- **source**: Set to the page URL. If `--source` was provided, use that value; otherwise use the input URL.
- **last_downloaded**: Set to today's date in YYYY-MM-DD format.

## Output Quality Standards

- Headings should use ATX style (`#`, `##`, etc.)
- Lists should use `-` for unordered items
- Tables should use standard markdown pipe syntax
- Links should be preserved in `[text](url)` format
- Clean, readable markdown that renders well on GitHub
- Frontmatter must be valid YAML
- No empty or meaningless output files
- Content should be the primary body text only — no navigation, footers, or site chrome
