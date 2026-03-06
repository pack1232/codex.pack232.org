---
name: doc-convert-to-markdown
description: Convert a document to Markdown, with support for multiple formats. Accepts a local file path or a URL. Determines the file type and delegates to the appropriate converter.
allowed-tools: Bash, Read, Write, Glob, Skill, AskUserQuestion
argument-hint: [path/to/file | path/to/folder/*.ext | URL] [--remove] [--ref] [--context "..."]
---

# Convert Document to Markdown

Convert a document file to clean Markdown format. Supports multiple file types and delegates to the appropriate conversion skill based on file extension. Accepts both local file paths and URLs (including Google Drive share links).

## Arguments

Parse `$ARGUMENTS` for:
- **file path, glob pattern, or URL** - the document(s) to convert (required). Can be a full path, relative path, filename, glob pattern (e.g., `folder/*.eml`), or a URL starting with `http://` or `https://`.
- **--remove** flag - if present, delete the original file after successful conversion. Ignored when the source is a URL.
- **--ref** flag - if present, create a reference-only markdown file instead of converting the document. The file contains only frontmatter and a link to the source — no content conversion is performed. See "Reference Mode" below.
- **--context "..."** - optional free-text hint (in quotes) that provides additional guidance. This can include what the document is, where to store it, tags to use, or any other context. See "Context Argument" below.

If no file path or URL is given, ask the user which file to convert.

## Batch Mode (Glob Patterns)

If the file path argument contains a glob wildcard character (`*`), treat it as a batch conversion request:

1. **Expand the pattern** using the Glob tool to find all matching files.
2. **Filter to supported formats** — only include files with supported extensions (`.docx`, `.pdf`, `.eml`). Skip unsupported files and warn the user about them.
3. **Skip already-converted files** — if a `.md` file with the same base name already exists alongside a matched file, skip it to avoid re-converting.
4. **Convert each file sequentially** — for each matched file, run the normal single-file conversion flow (steps 5-11 below). Pass through any `--remove`, `--ref`, and `--context` flags to each conversion.
5. **Print a summary** at the end:
   - Total files found matching the pattern
   - Number successfully converted
   - Number skipped (already converted or unsupported format)
   - Number failed (with error details)
   - List of all output `.md` file paths

Batch mode is especially useful for `.eml` files where the user has exported a folder of emails. Example: `/doc-convert-to-markdown docs/Events & Activities/Winter Camping/emails/*.eml`

**Note:** `--ref` mode and URL sources are not supported in batch mode. If `--ref` is combined with a glob pattern, inform the user and stop. If the pattern matches zero files, inform the user and stop.

## Context Argument (`--context`)

The `--context` argument accepts a free-text string (in quotes) that guides the skill's behavior. It is advisory — the skill uses it as additional signal alongside its own analysis. The context string can influence any combination of the following:

### What It Can Influence

| Area | Example context | Effect |
|------|----------------|--------|
| **Destination folder** | `"this is a form for camp registration"` | Biases destination folder detection toward `Forms & Policies` or `Campout Resources` |
| **Title** | `"this is the annual recharter guide"` | Helps derive a more accurate title when the filename is cryptic |
| **Description** | `"BSA guide for new den leaders"` | Seeds the description with user-provided understanding of the document |
| **Tags** | `"related to pinewood derby rules"` | Influences tag selection toward relevant terms |
| **Category/subfolder** | `"put this in Training/Positions/Cubmaster"` | Explicit path overrides destination folder detection — skip the keyword scoring and use the specified path directly |

### How It Works

1. **Parse** the `--context` value from `$ARGUMENTS`. The value is everything between the quotes after `--context`.
2. **Check for explicit path directives** — if the context contains a path-like string (e.g., `"store in Training/Positions/Cubmaster"`, `"put in Forms & Policies"`), treat it as an explicit destination and skip the keyword-based destination folder detection. Create the directory if it does not exist.
3. **Feed into metadata generation** — pass the context string to all auto-detection steps (title derivation, description generation, tag inference) as supplemental information. The context should be weighted alongside (not replace) content-based analysis.
4. **Feed into destination folder detection** — if no explicit path was given, include the context string in the keyword scoring alongside title, description, tags, and body content.

### Interaction with Other Flags

- Works with both normal conversion and `--ref` mode.
- Works with both URL and local file sources.
- When combined with `--ref`, the context is especially valuable since there is no document content to analyze — it becomes the primary signal for metadata and destination.

## Reference Mode (`--ref`)

When `--ref` is provided, the skill creates a lightweight reference markdown file instead of downloading and converting the document. This is ideal for forms, large documents, or any resource where full conversion isn't practical but you still want a searchable record with a link to the source.

### How It Works

1. **No download or conversion** — the document is not downloaded or processed.
2. **Derive metadata from the URL or file path:**
   - **Filename**: Extract from the URL path (last segment, URL-decoded) or local file path.
   - **Title**: Derive a readable title from the filename by splitting on camelCase/PascalCase boundaries, hyphens, underscores, and removing catalog number prefixes (e.g., `524-501_Adult_Application.pdf` → `Adult Application`, `33221_CubScoutLeaderBook.pdf` → `Cub Scout Leader Book`).
   - **Original format**: From the file extension.
3. **Ask the user** to confirm or adjust the title and provide a brief description (1-2 sentences) for the document. If the user provides no description, generate a best-guess from the title.
4. **Ask the user for tags** or infer 2-5 tags from the title and description.
5. **Run destination folder detection** using the title, description, and tags (same keyword map as full conversions).
6. **Write the reference file** to the selected destination folder.

### Reference File Format

The generated `.md` file contains frontmatter and a short body with a link to the source:

```markdown
---
title: ""
description: ""
source_file: ""
converted_date: ""
original_format: ""
author: "Unknown"
tags: []
category: ""
draft: false
source: ""
type: "reference"
---

> This document has not been converted to markdown. Use the link below to access the original.
>
> **[View or download the original document](<source URL or local path>)**
```

Key differences from a full conversion:
- The `type: "reference"` field distinguishes this from a fully converted document.
- The body contains only a blockquote with a link — no converted content.
- The `author` defaults to `"Unknown"` (no content to extract from).
- The `--remove` flag is ignored in reference mode.

### Reference Mode with Local Files

When `--ref` is used with a local file path instead of a URL:
- The `source` field is omitted (no URL to record).
- The body link points to the original file using a relative path from the destination folder.
- The `last_downloaded` field is omitted.

## URL Detection and Download

If the input starts with `http://` or `https://`, treat it as a URL source:

### Google Drive Link Detection

Google Drive share links must be converted to direct download URLs before downloading:
- `https://drive.google.com/file/d/<FILE_ID>/view...` → `https://drive.google.com/uc?export=download&id=<FILE_ID>`
- `https://drive.google.com/open?id=<FILE_ID>` → `https://drive.google.com/uc?export=download&id=<FILE_ID>`

Extract the `<FILE_ID>` from the URL and construct the direct download URL. Store the **original** user-provided URL separately (it will go into the `source` frontmatter field, not the transformed URL).

### Download Process

1. Download the file to `docs/tmp/` (within the project) using `curl -L -J -o`:
   - `-L` follows redirects
   - `-J` uses the server-suggested filename from the Content-Disposition header
   - Use `-D docs/tmp/doc-headers.txt` to capture response headers
   - Create `docs/tmp/` if it does not already exist
2. Determine the filename:
   - First, check the Content-Disposition header in `docs/tmp/doc-headers.txt` for a `filename=` value
   - If no Content-Disposition filename, derive from the URL path (last path segment before query params)
   - If the filename still has no recognizable extension, inspect the Content-Type header to map to an extension (e.g., `application/pdf` → `.pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` → `.docx`)
   - Rename the downloaded file to have the correct filename/extension if needed
3. Verify the download:
   - File must exist and be non-empty
   - File must have a supported extension (`.pdf`, `.docx`, or `.eml`)
   - If verification fails, report the error to the user and stop

### URL Source Behavior

- The `--remove` flag is **ignored** when the source is a URL (do not attempt to delete a remote resource)
- The original user-provided URL is passed to the sub-skill via `--source <url>` so it can be recorded in frontmatter

## Supported Formats

| Extension / Type | Converter |
|------------------|-----------|
| `.docx`          | Invoke the `docx-to-md` skill |
| `.pdf`           | Invoke the `pdf-to-md` skill |
| `.eml`           | Invoke the `eml-to-md` skill |
| Web page (URL with no file extension, or `.html`/`.htm`) | Invoke the `html-to-md` skill |

If the input is a URL with no recognizable document extension (no `.pdf`, `.docx`, etc.), treat it as a web page and delegate to the `html-to-md` skill. This skill fetches the page and extracts the primary body content.

If the file extension is not in the table above and the input is not a web page URL, inform the user that the format is not yet supported and list the currently supported formats.

## Frontmatter Specification

Every generated markdown file MUST include YAML frontmatter at the top of the file. The converter skills are responsible for generating this frontmatter block.

### Required Fields

```yaml
---
title: ""          # Auto-detected from document content (first heading, title metadata, or derived from filename)
description: ""    # Brief 1-2 sentence summary of the document content
source_file: ""    # Original filename with extension (e.g., "MyDocument.docx")
converted_date: "" # Date of conversion in YYYY-MM-DD format
original_format: "" # File extension without dot (e.g., "docx", "pdf")
author: ""         # Auto-detected from document metadata or content if available, otherwise "Unknown"
tags: []           # 2-5 relevant lowercase tags derived from the content (e.g., ["camping", "gear", "checklist"])
category: ""       # Inferred from the parent directory name (e.g., "Campout Resources", "Events & Activities")
draft: false       # Always set to false for conversions
---
```

### Optional Fields

```yaml
source: ""         # Only included when document was downloaded from a URL. Contains the original user-provided URL (not a transformed direct-download URL).
last_downloaded: "" # Only included when document was downloaded from a URL. Date the file was downloaded in YYYY-MM-DD format.
```

### Auto-Detection Rules

- **title**: Use the first `#` heading in the converted content. If none, derive a readable title from the filename (e.g., `Pack232RecommendedTentCampingGear` → `Pack 232 Recommended Tent Camping Gear`). Remove the `#` heading from the body if it was used as the title to avoid duplication.
- **description**: Generate a concise summary based on the document content. Keep it to 1-2 sentences.
- **author**: Extract from document metadata if available, or from content (e.g., "by Author Name"). Use `"Unknown"` if not determinable.
- **tags**: Analyze the content and pick 2-5 descriptive lowercase tags. Focus on the subject matter.
- **category**: Use the immediate parent directory name of the source file. If the file was moved by destination folder detection, update to match the new parent directory.
- **source**: Only present when the document was converted from a URL. Set to the original URL the user provided.
- **last_downloaded**: Only present when the document was converted from a URL. Set to today's date in YYYY-MM-DD format.

## Steps

1. **Parse arguments** - Extract the file path or URL, check for `--remove`, `--ref`, and `--context "..."` from `$ARGUMENTS`. If `--context` is present, extract the quoted string value.

2. **Check for reference mode** - If `--ref` is present, follow the "Reference Mode" section above instead of the normal conversion flow. Skip to step 2a.

   **2a. Reference mode flow:**
   1. Determine if the input is a URL or local file path.
   2. Extract the filename from the URL path (URL-decoded) or local file path.
   3. Derive a readable title from the filename. Use `--context` to improve the title if the filename is cryptic.
   4. Ask the user to confirm the title and provide a description via `AskUserQuestion`. Pre-fill suggestions using `--context` if provided.
   5. Infer tags from the title, description, and `--context`; present them for user confirmation.
   6. Run destination folder detection (or use explicit path from `--context` if provided).
   7. Write the reference `.md` file to the selected folder using the reference file format.
   8. Report the output file path and frontmatter to the user.
   9. **Stop** — do not continue to the normal conversion steps.

3. **Detect input type** - Check if the input starts with `http://` or `https://`:
   - If yes → URL source (go to step 4)
   - If no → local file path (skip to step 5)

4. **Download from URL (downloadable documents only)** - If the URL points to a downloadable document (has a `.pdf`, `.docx`, or similar extension), follow the "URL Detection and Download" section above:
   - Check for Google Drive links and transform if needed (preserve original URL)
   - Download to `docs/tmp/`
   - Resolve filename and extension
   - Verify download succeeded
   - The downloaded file in `docs/tmp/` becomes the local file path for subsequent steps
   - If the URL has no document extension (web page), **skip this step** — the `html-to-md` skill handles fetching directly.

5. **Locate the file** - If the path is just a filename or relative, use Glob with `**/<filename>` to find it. Verify the file exists.

6. **Determine format** - Check the file extension (case-insensitive). If the source is a URL with no recognizable document extension (no `.pdf`, `.docx`), treat it as a web page (skip the download step — the `html-to-md` skill fetches the content directly).

7. **Convert** - Based on the format, invoke the appropriate sub-skill using the Skill tool:
   - `.docx` → Invoke the `docx-to-md` skill
   - `.pdf` → Invoke the `pdf-to-md` skill
   - `.eml` → Invoke the `eml-to-md` skill
   - Web page → Invoke the `html-to-md` skill (pass the URL directly; no download step needed)
   - If the source was a URL, append `--source <original_url>` to the skill arguments so the sub-skill includes the `source` field in frontmatter.

8. **Verify output** - Confirm the `.md` file was created successfully and contains valid YAML frontmatter.

9. **Destination folder detection (URL sources only)** - If the source was a URL, run the destination folder detection process to place the file in the appropriate `docs/` subfolder. If `--context` specifies an explicit path, use that directly instead. See the "Destination Folder Detection" section below.

10. **Remove original (if applicable)** - Only if `--remove` flag was provided AND the source was a local file (not a URL) AND the `.md` output file exists and is non-empty:
    - Show the user which file will be deleted and ask for confirmation before deleting.
    - Delete the original file using Bash `rm`.
    - Confirm deletion to the user.

11. **Report** - Show the user:
    - The output `.md` file path (final location after any move).
    - The frontmatter that was generated.
    - The source URL (if applicable).
    - Whether the original was removed (if `--remove` was used with a local file).

## Destination Folder Detection

When a document is converted from a URL, the output `.md` file starts in `docs/tmp/`. This section determines where to place it within the `docs/` directory tree.

### Keyword Map

Analyze the converted markdown content (title, description, tags, and body text) against this keyword map:

| Folder | Keywords |
|--------|----------|
| `Advancement` | rank, advancement, badge, merit, trail to first class, scout rank, requirements, award |
| `Campout Resources` | campout, camping, tent, outdoor, campfire, campsite, packing list, sleeping bag, gear list |
| `Events & Activities` | event, activity, derby, blue and gold, field trip, outing, parade, celebration, ceremony |
| `Forms & Policies` | form, policy, permission, waiver, consent, registration, application, agreement, rules |
| `Fundraising` | fundraiser, fundraising, popcorn, wreath, donation, sales, money, profit |
| `Gear & Apparel` | gear, uniform, apparel, clothing, shirt, hat, patch, equipment, supplies |
| `Lawson Lake` | lawson, lake, cabin, property, reservation |
| `Leadership` | leader, committee, chair, coordinator, den leader, cubmaster, scoutmaster, akela |
| `Marketing & Recruitment` | marketing, recruitment, flyer, brochure, poster, join, sign up, new families |
| `Meetings` | meeting, agenda, minutes, den meeting, pack meeting, schedule |
| `Membership` | membership, roster, registration, recharter, dues, member |
| `Photo Gallery` | photo, picture, gallery, image |
| `Service Projects` | service, volunteer, community, project, cleanup, food drive |
| `Training` | training, ypt, youth protection, certification, course, baloo, owls |
| `Treasurer` | treasurer, budget, finance, expense, receipt, reimbursement, payment, bank |

### Detection Process

1. If `--context` specifies an explicit destination path (e.g., `"put in Forms & Policies"`, `"store in Training/Positions/Cubmaster"`), use that path directly — create the directory if needed and skip to step 5.
2. Score each folder by counting keyword matches across the title, description, tags, `--context` string (if provided), and first ~500 words of body content (case-insensitive).
3. Select the folder with the highest score.
4. Present the suggested folder to the user via `AskUserQuestion`:
   - Show the top suggestion and why (matched keywords)
   - Include 2-3 runner-up options
   - Include an "Other" option so the user can specify a different path
5. If no folder scores any matches, skip the suggestion and directly ask the user to pick from the list of folders.
6. Move the `.md` file to the selected `docs/<folder>/` directory.
7. Update the `category` field in the frontmatter to match the new parent directory name.
