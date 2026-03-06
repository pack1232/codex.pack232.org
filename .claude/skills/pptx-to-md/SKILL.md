---
name: pptx-to-md
description: Convert a .pptx PowerPoint presentation to clean .md Markdown. Use when the user wants to convert a PowerPoint file to markdown format.
allowed-tools: Bash, Read, Write, Glob
argument-hint: [path/to/file.pptx] [--source URL]
---

# Convert .pptx to Markdown

Convert the specified PowerPoint presentation (.pptx) to a clean Markdown (.md) file with YAML frontmatter. Each slide becomes a section in the markdown output.

## Input

Parse `$ARGUMENTS` for:
- **file path** - path to a `.pptx` file (required). If no argument is given, ask the user which `.pptx` file to convert.
- **--source URL** - optional. When provided, the URL is recorded in the `source` frontmatter field. This is set by the `doc-convert-to-markdown` parent skill when the document was downloaded from a URL.

If the path is relative or just a filename, search the project for the file using Glob.

## Conversion Steps

1. **Locate the file** - Verify the .pptx file exists. If only a filename was given, use Glob to find it with `**/$ARGUMENTS`.

2. **Ensure the conversion tool is available** - Install `python-pptx` if not present:
   ```bash
   pip3 install --user --break-system-packages python-pptx 2>/dev/null
   ```

3. **Convert the file** - Run a Python script using `python-pptx` to extract slide content:
   ```python
   from pptx import Presentation
   from pptx.util import Inches, Pt
   import sys

   prs = Presentation('<input_path>')
   output_lines = []

   for slide_num, slide in enumerate(prs.slides, 1):
       title = ""
       body_texts = []
       notes_text = ""

       # Extract title
       if slide.shapes.title:
           title = slide.shapes.title.text.strip()

       # Extract text from all shapes
       for shape in slide.shapes:
           if shape.has_text_frame:
               # Skip the title shape (already captured)
               if shape.shape_id == (slide.shapes.title.shape_id if slide.shapes.title else None):
                   continue
               for paragraph in shape.text_frame.paragraphs:
                   text = paragraph.text.strip()
                   if text:
                       # Check if it looks like a bullet point
                       if paragraph.level > 0:
                           body_texts.append("  " * paragraph.level + "- " + text)
                       else:
                           body_texts.append("- " + text)

           # Extract tables
           if shape.has_table:
               table = shape.table
               rows = []
               for row in table.rows:
                   cells = [cell.text.strip() for cell in row.cells]
                   rows.append("| " + " | ".join(cells) + " |")
               if rows:
                   # Add header separator after first row
                   header_sep = "| " + " | ".join(["---"] * len(table.rows[0].cells)) + " |"
                   body_texts.append(rows[0])
                   body_texts.append(header_sep)
                   body_texts.extend(rows[1:])

       # Extract speaker notes
       if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
           notes_text = slide.notes_slide.notes_text_frame.text.strip()

       # Format slide section
       slide_title = f"## Slide {slide_num}: {title}" if title else f"## Slide {slide_num}"
       output_lines.append(slide_title)
       output_lines.append("")

       if body_texts:
           output_lines.extend(body_texts)
           output_lines.append("")

       if notes_text:
           output_lines.append(f"> **Speaker notes:** {notes_text}")
           output_lines.append("")

   print("\n".join(output_lines))
   ```

4. **Handle empty presentations** - If no text content was extracted from any slide (total text under 50 characters), create a reference-only `.md` file with `type: "reference"` in frontmatter, similar to image-only PDFs.

5. **Clean up the output** - Polish the extracted content:
   - Remove duplicate blank lines (collapse 3+ to 2)
   - Remove trailing whitespace
   - Fix any encoding issues with special characters
   - Ensure consistent list formatting

6. **Generate frontmatter** - Add YAML frontmatter to the top of the file following the rules below.

7. **Write the output** - Save the cleaned markdown (with frontmatter) to the same directory as the source file, with the `.md` extension replacing `.pptx`.

8. **Show the user the result** - Display the output file path, slide count, and a brief summary of the content.

## Frontmatter Specification

Every generated markdown file MUST begin with a YAML frontmatter block. Generate the following fields:

```yaml
---
title: ""          # Auto-detected (see rules below)
description: ""    # Brief 1-2 sentence summary of the presentation content
source_file: ""    # Original filename with extension (e.g., "MyPresentation.pptx")
converted_date: "" # Today's date in YYYY-MM-DD format
original_format: "pptx"
author: ""         # From presentation metadata or content if available, otherwise "Unknown"
tags: []           # 2-5 relevant lowercase tags derived from the content
category: ""       # Immediate parent directory name of the source file
slide_count: 0     # Total number of slides in the presentation
draft: false
source: ""         # Optional: only include if --source was provided. Contains the original URL.
last_downloaded: "" # Optional: only include if --source was provided. Today's date in YYYY-MM-DD format.
---
```

### Auto-Detection Rules

- **title**: Use the title from the first slide if it exists and is meaningful. If the first slide has no title or it's generic (e.g., just "Slide 1"), derive a readable title from the filename by splitting on camelCase/PascalCase boundaries, hyphens, and underscores. Do NOT include the slide heading in the body if it was used as the document title.
- **description**: Generate a concise 1-2 sentence summary of the presentation's topic and purpose.
- **author**: Check presentation metadata (core_properties.author) if accessible via python-pptx. Otherwise look for author mentions in slide content. Use `"Unknown"` if not found.
- **tags**: Analyze the slide content and assign 2-5 descriptive lowercase tags focused on subject matter.
- **category**: Use the immediate parent directory name of the source file.
- **slide_count**: Total number of slides in the presentation.
- **source**: Only include this field if `--source <url>` was passed in the arguments. Omit entirely if not provided.
- **last_downloaded**: Only include this field if `--source <url>` was passed in the arguments. Omit entirely if not provided.

## Output Quality Standards

- Each slide should be a `##` heading with slide number and title
- Bullet points should use `-` for unordered items with proper indentation for sub-bullets
- Tables should use standard markdown pipe syntax
- Speaker notes should be in blockquote format
- Clean, readable markdown that renders well on GitHub
- Frontmatter must be valid YAML
