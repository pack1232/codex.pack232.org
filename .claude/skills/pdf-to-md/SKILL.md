---
name: pdf-to-md
description: Convert a .pdf document to clean .md Markdown. Use when the user wants to convert a PDF document to markdown format.
allowed-tools: Bash, Read, Write, Glob
argument-hint: [path/to/file.pdf] [--source URL]
---

# Convert .pdf to Markdown

Convert the specified PDF document to a clean Markdown (.md) file with YAML frontmatter.

## Input

Parse `$ARGUMENTS` for:
- **file path** - path to a `.pdf` file (required). If no argument is given, ask the user which `.pdf` file to convert.
- **--source URL** - optional. When provided, the URL is recorded in the `source` frontmatter field. This is set by the `doc-convert-to-markdown` parent skill when the document was downloaded from a URL.

If the path is relative or just a filename, search the project for the file using Glob.

## Conversion Steps

1. **Locate the file** - Verify the .pdf file exists. If only a filename was given, use Glob to find it with `**/$ARGUMENTS`.

2. **Ensure the conversion tools are available** - Use a Python virtual environment with `pymupdf4llm` installed:
   ```
   python3 -m venv /tmp/docx-conv 2>/dev/null
   /tmp/docx-conv/bin/pip install -q pymupdf4llm 2>/dev/null
   ```

3. **Convert the file** - Run pymupdf4llm via Python to produce markdown:
   ```python
   import pymupdf4llm
   md = pymupdf4llm.to_markdown('<input_path>')
   print(md)
   ```

4. **Handle image-only / scanned PDFs** - If the extracted text is empty or nearly empty (under 50 characters of actual text content), inform the user that the PDF appears to be a scanned image and cannot be converted to meaningful markdown text. Suggest OCR tools as an alternative. Do NOT create an empty or near-empty .md file.

5. **Clean up the output** - The raw pymupdf4llm output may need fixing:
   - Remove the "Consider using the pymupdf_layout package" warning line if present
   - Ensure the first meaningful line is promoted to a `#` heading if it looks like a title (standalone line at the top, often bold or larger text)
   - Remove excessive blank lines (collapse 3+ consecutive blank lines to 2)
   - Fix broken words split across lines where appropriate
   - Remove trailing whitespace from lines
   - Preserve links, tables, and list formatting from pymupdf4llm

6. **Generate frontmatter** - Add YAML frontmatter to the top of the file following the rules below.

7. **Write the output** - Save the cleaned markdown (with frontmatter) to the same directory as the source file, with the `.md` extension replacing `.pdf`.

8. **Show the user the result** - Display the output file path and a brief summary of the content (first heading or first few lines).

## Frontmatter Specification

Every generated markdown file MUST begin with a YAML frontmatter block. Generate the following fields:

```yaml
---
title: ""          # Auto-detected (see rules below)
description: ""    # Brief 1-2 sentence summary of the document content
source_file: ""    # Original filename with extension (e.g., "MyDocument.pdf")
converted_date: "" # Today's date in YYYY-MM-DD format
original_format: "pdf"
author: ""         # From document content or metadata if available, otherwise "Unknown"
tags: []           # 2-5 relevant lowercase tags derived from the content
category: ""       # Immediate parent directory name of the source file
draft: false
source: ""         # Optional: only include if --source was provided. Contains the original URL.
last_downloaded: "" # Optional: only include if --source was provided. Today's date in YYYY-MM-DD format.
---
```

### Auto-Detection Rules

- **title**: Use the first `#` heading in the converted content. If none, derive a readable title from the filename by splitting on camelCase/PascalCase boundaries, hyphens, and underscores (e.g., `PinewoodDerbyFAQ` → `Pinewood Derby FAQ`). When the title comes from a `#` heading in the body, REMOVE that heading from the body to avoid duplication.
- **description**: Generate a concise 1-2 sentence summary of the document's purpose and content.
- **author**: Look for patterns like "by [Name]", "Author: [Name]", or "written by [Name]" in the content. Also check PDF metadata if accessible via pymupdf. Use `"Unknown"` if not found.
- **tags**: Analyze the content and assign 2-5 descriptive lowercase tags focused on subject matter (e.g., `["pinewood derby", "faq", "racing"]`).
- **category**: Use the immediate parent directory name of the source file (e.g., if the file is in `docs/Events & Activities/Pinewood Derby/`, the category is `"Pinewood Derby"`).
- **source**: Only include this field if `--source <url>` was passed in the arguments. Set it to the provided URL. If `--source` was not provided, omit the `source` field entirely from the frontmatter (do not include it as empty).
- **last_downloaded**: Only include this field if `--source <url>` was passed in the arguments. Set it to today's date in YYYY-MM-DD format. If `--source` was not provided, omit this field entirely.

## Output Quality Standards

- Headings should use ATX style (`#`, `##`, etc.)
- Lists should use `-` for unordered items
- Tables should use standard markdown pipe syntax
- Links should be preserved in `[text](url)` format
- Clean, readable markdown that renders well on GitHub
- Frontmatter must be valid YAML
- No empty or meaningless output files
