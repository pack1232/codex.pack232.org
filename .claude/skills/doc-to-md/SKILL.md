---
name: doc-to-md
description: Convert a legacy .doc Word document to clean .md Markdown. Use when the user wants to convert a .doc file to markdown format.
allowed-tools: Bash, Read, Write, Glob
argument-hint: [path/to/file.doc] [--source URL]
---

# Convert .doc to Markdown

Convert the specified legacy Word document (.doc) to a clean Markdown (.md) file with YAML frontmatter.

## Input

Parse `$ARGUMENTS` for:
- **file path** - path to a `.doc` file (required). If no argument is given, ask the user which `.doc` file to convert.
- **--source URL** - optional. When provided, the URL is recorded in the `source` frontmatter field. This is set by the `doc-convert-to-markdown` parent skill when the document was downloaded from a URL.

If the path is relative or just a filename, search the project for the file using Glob.

## Conversion Steps

1. **Locate the file** - Verify the .doc file exists. If only a filename was given, use Glob to find it with `**/$ARGUMENTS`.

2. **Ensure the conversion tool is available** - Install `olefile` if not present:
   ```bash
   pip3 install --user --break-system-packages olefile 2>/dev/null
   ```

3. **Convert the file** - Use Python with `olefile` to extract text from the Word Document stream:
   ```python
   import olefile
   import re

   ole = olefile.OleFileIO('<input_path>')
   data = ole.openstream('WordDocument').read()
   ole.close()

   # Extract printable ASCII text from the binary stream
   raw = ""
   for byte in data:
       if 0x20 <= byte < 0x7F:
           raw += chr(byte)
       elif byte == 0x0D:
           raw += '\n'
       elif byte == 0x09:
           raw += '\t'
       else:
           raw += '\x00'

   # Split on null sequences, keep segments with >60% alphabetic content
   segments = re.split(r'\x00+', raw)
   good = [s.strip() for s in segments
           if len(s.strip()) > 20 and
           sum(1 for c in s if c.isalpha() or c.isspace()) / len(s) > 0.6]
   text = '\n'.join(good)
   ```
   Filter out binary residue: Word field codes, font names, and lines that are mostly non-alphabetic characters.

4. **Handle conversion failures** - If olefile fails or produces empty/near-empty output (under 50 characters of actual text):
   - Create a **reference-only** `.md` file with `type: "reference"` in frontmatter
   - The body should contain a blockquote noting the file could not be converted:
     ```markdown
     > This document could not be converted to markdown (legacy .doc format with unsupported content).
     > The original file has been preserved in the archive.
     ```
   - Continue to step 6 for frontmatter generation.

5. **Clean up the output** - The extracted plain text needs formatting as markdown:
   - Identify lines that look like section titles (ALL CAPS lines, or short standalone lines followed by body text) and convert them to markdown headings (`##`)
   - Preserve paragraph breaks (blank lines between paragraphs)
   - Convert any obvious list patterns (lines starting with `-`, `*`, numbers, or bullet characters) to proper markdown lists
   - Remove trailing whitespace from lines
   - Collapse 3+ consecutive blank lines to 2
   - If the first meaningful line looks like a document title, promote it to a `#` heading

6. **Generate frontmatter** - Add YAML frontmatter to the top of the file following the rules below.

7. **Write the output** - Save the cleaned markdown (with frontmatter) to the same directory as the source file, with the `.md` extension replacing `.doc` (or `.DOC`).

8. **Show the user the result** - Display the output file path and a brief summary of the content.

## Frontmatter Specification

Every generated markdown file MUST begin with a YAML frontmatter block. Generate the following fields:

```yaml
---
title: ""          # Auto-detected (see rules below)
description: ""    # Brief 1-2 sentence summary of the document content
source_file: ""    # Original filename with extension (e.g., "MyDocument.doc")
converted_date: "" # Today's date in YYYY-MM-DD format
original_format: "doc"
author: ""         # From document content if available, otherwise "Unknown"
tags: []           # 2-5 relevant lowercase tags derived from the content
category: ""       # Immediate parent directory name of the source file
draft: false
source: ""         # Optional: only include if --source was provided. Contains the original URL.
last_downloaded: "" # Optional: only include if --source was provided. Today's date in YYYY-MM-DD format.
---
```

### Auto-Detection Rules

- **title**: Use the first `#` heading in the converted content. If none, derive a readable title from the filename by splitting on camelCase/PascalCase boundaries, hyphens, and underscores (e.g., `CubScoutWinterCampingfoodorder` → `Cub Scout Winter Camping Food Order`). When the title comes from a `#` heading in the body, REMOVE that heading from the body to avoid duplication.
- **description**: Generate a concise 1-2 sentence summary of the document's purpose and content.
- **author**: Look for patterns like "by [Name]", "Author: [Name]", or "written by [Name]" in the content. Use `"Unknown"` if not found.
- **tags**: Analyze the content and assign 2-5 descriptive lowercase tags focused on subject matter.
- **category**: Use the immediate parent directory name of the source file.
- **source**: Only include this field if `--source <url>` was passed in the arguments. Set it to the provided URL. If `--source` was not provided, omit the `source` field entirely from the frontmatter.
- **last_downloaded**: Only include this field if `--source <url>` was passed in the arguments. Set it to today's date in YYYY-MM-DD format. If `--source` was not provided, omit this field entirely.

## Output Quality Standards

- Headings should use ATX style (`#`, `##`, etc.)
- Lists should use `-` for unordered items
- Clean, readable markdown that renders well on GitHub
- Frontmatter must be valid YAML
- Reference-only files are acceptable for docs that olefile cannot extract text from
