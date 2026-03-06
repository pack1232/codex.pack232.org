---
name: docx-to-md
description: Convert a .docx Word document to clean .md Markdown. Use when the user wants to convert a Word document to markdown format.
allowed-tools: Bash, Read, Write, Glob
argument-hint: [path/to/file.docx] [--source URL]
---

# Convert .docx to Markdown

Convert the specified Word document (.docx) to a clean Markdown (.md) file with YAML frontmatter.

## Input

Parse `$ARGUMENTS` for:
- **file path** - path to a `.docx` file (required). If no argument is given, ask the user which `.docx` file to convert.
- **--source URL** - optional. When provided, the URL is recorded in the `source` frontmatter field. This is set by the `doc-convert-to-markdown` parent skill when the document was downloaded from a URL.

If the path is relative or just a filename, search the project for the file using Glob.

## Conversion Steps

1. **Locate the file** - Verify the .docx file exists. If only a filename was given, use Glob to find it with `**/$ARGUMENTS`.

2. **Ensure the conversion tool is available** - Use a Python virtual environment with `mammoth` installed:
   ```
   python3 -m venv /tmp/docx-conv 2>/dev/null
   /tmp/docx-conv/bin/pip install -q mammoth 2>/dev/null
   ```

3. **Convert the file** - Run mammoth via Python to produce raw markdown:
   ```python
   import mammoth
   with open('<input_path>', 'rb') as f:
       result = mammoth.convert_to_markdown(f)
   print(result.value)
   ```

4. **Clean up the output** - Mammoth's markdown output often has issues that need fixing:
   - Remove unnecessary backslash escapes (e.g., `\-`, `\.`, `\(`, `\)`)
   - Convert bold markers (`__text__`) to proper markdown headings (`# text`) where they represent section titles (standalone bold lines)
   - Preserve inline bold as `**text**`
   - Remove trailing whitespace
   - Ensure consistent blank lines between sections
   - Fix smart quotes/special characters if needed

5. **Generate frontmatter** - Add YAML frontmatter to the top of the file following the rules below.

6. **Write the output** - Save the cleaned markdown (with frontmatter) to the same directory as the source file, with the `.md` extension replacing `.docx`.

7. **Show the user the result** - Display the output file path and a brief summary of the content.

## Frontmatter Specification

Every generated markdown file MUST begin with a YAML frontmatter block. Generate the following fields:

```yaml
---
title: ""          # Auto-detected (see rules below)
description: ""    # Brief 1-2 sentence summary of the document content
source_file: ""    # Original filename with extension (e.g., "MyDocument.docx")
converted_date: "" # Today's date in YYYY-MM-DD format
original_format: "docx"
author: ""         # From document content or metadata if available, otherwise "Unknown"
tags: []           # 2-5 relevant lowercase tags derived from the content
category: ""       # Immediate parent directory name of the source file
draft: false
source: ""         # Optional: only include if --source was provided. Contains the original URL.
last_downloaded: "" # Optional: only include if --source was provided. Today's date in YYYY-MM-DD format.
---
```

### Auto-Detection Rules

- **title**: Use the first `#` heading in the converted content. If none, derive a readable title from the filename by splitting on camelCase/PascalCase boundaries and underscores (e.g., `Pack232RecommendedTentCampingGear` → `Pack 232 Recommended Tent Camping Gear`). When the title comes from a `#` heading in the body, REMOVE that heading from the body to avoid duplication.
- **description**: Generate a concise 1-2 sentence summary of the document's purpose and content.
- **author**: Look for patterns like "by [Name]", "Author: [Name]", or "written by [Name]" in the content. Use `"Unknown"` if not found.
- **tags**: Analyze the content and assign 2-5 descriptive lowercase tags focused on subject matter (e.g., `["camping", "gear", "checklist"]`).
- **category**: Use the immediate parent directory name of the source file (e.g., if the file is in `docs/Campout Resources/`, the category is `"Campout Resources"`).
- **source**: Only include this field if `--source <url>` was passed in the arguments. Set it to the provided URL. If `--source` was not provided, omit the `source` field entirely from the frontmatter (do not include it as empty).
- **last_downloaded**: Only include this field if `--source <url>` was passed in the arguments. Set it to today's date in YYYY-MM-DD format. If `--source` was not provided, omit this field entirely.

## Output Quality Standards

- Headings should use ATX style (`#`, `##`, etc.) not bold text for section titles
- Lists should use `-` for unordered items
- No excessive escape characters
- Clean, readable markdown that renders well on GitHub
- Frontmatter must be valid YAML
