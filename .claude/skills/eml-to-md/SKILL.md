---
name: eml-to-md
description: Convert .eml email files to clean .md Markdown. Use when the user wants to convert saved email files to markdown format. Supports single files and batch conversion via glob patterns.
allowed-tools: Bash, Read, Write, Glob
argument-hint: [path/to/file.eml | path/to/folder/*.eml] [--source URL] [--account email]
---

# Convert .eml to Markdown

Convert saved email files (.eml) to clean Markdown (.md) files with YAML frontmatter that includes email-specific metadata.

## Input

Parse `$ARGUMENTS` for:
- **file path or glob pattern** - path to a `.eml` file or a glob pattern matching multiple `.eml` files (required). If no argument is given, ask the user which `.eml` file(s) to convert.
- **--source URL** - optional. When provided, the URL is recorded in the `source` frontmatter field. This is set by the `doc-convert-to-markdown` parent skill when the document was downloaded from a URL. Only applicable in single-file mode.
- **--account email** - optional. The email account these emails were downloaded/exported from (e.g., `cubmaster@pack232.com`). When provided, recorded in the `email_account` frontmatter field. Applies to all files in batch mode.

If the path is relative or just a filename, search the project for the file using Glob.

## Batch Mode

If the argument contains a glob pattern (contains `*`), expand it using the Glob tool and convert each matching `.eml` file individually. Process files sequentially. At the end, print a summary showing how many files were converted and list each output file path.

If no `.eml` files match the pattern, inform the user and stop.

## Conversion Steps

For each `.eml` file:

1. **Locate the file** - Verify the .eml file exists. If only a filename was given, use Glob to find it with `**/$ARGUMENTS`.

2. **Parse the email** - Use Python's built-in `email` module (no external dependencies required):
   ```bash
   python3 << 'PYEOF'
   import email
   import email.policy
   import json
   import sys
   from email.utils import parsedate_to_datetime

   with open('<input_path>', 'rb') as f:
       msg = email.message_from_binary_file(f, policy=email.policy.default)

   # Extract headers
   headers = {
       'from': str(msg['From'] or ''),
       'to': str(msg['To'] or ''),
       'cc': str(msg['Cc'] or ''),
       'date': str(msg['Date'] or ''),
       'subject': str(msg['Subject'] or '(No Subject)'),
       'message_id': str(msg['Message-ID'] or ''),
       'in_reply_to': str(msg['In-Reply-To'] or ''),
   }

   # Parse date to ISO format
   try:
       dt = parsedate_to_datetime(msg['Date'])
       headers['date_iso'] = dt.strftime('%Y-%m-%d')
       headers['date_display'] = dt.strftime('%B %d, %Y at %I:%M %p')
   except:
       headers['date_iso'] = ''
       headers['date_display'] = headers['date']

   # Extract body - prefer text/plain, fall back to text/html
   body = ''
   html_body = ''
   if msg.is_multipart():
       for part in msg.walk():
           content_type = part.get_content_type()
           if content_type == 'text/plain' and not body:
               body = part.get_content()
           elif content_type == 'text/html' and not html_body:
               html_body = part.get_content()
   else:
       if msg.get_content_type() == 'text/html':
           html_body = msg.get_content()
       else:
           body = msg.get_content()

   # List attachments
   attachments = []
   if msg.is_multipart():
       for part in msg.walk():
           if part.get_content_disposition() == 'attachment':
               filename = part.get_filename()
               if filename:
                   attachments.append(filename)

   result = {
       'headers': headers,
       'body': body,
       'html_body': html_body,
       'attachments': attachments,
   }
   print(json.dumps(result))
   PYEOF
   ```

3. **Convert HTML body if needed** - If no plain text body was found but an HTML body exists, convert the HTML to markdown. Use Python with a simple tag-stripping approach:
   ```bash
   python3 << 'PYEOF'
   import re
   import html as html_module

   html_content = """<the html body>"""

   # Remove style and script blocks
   text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
   text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)

   # Convert common HTML elements to markdown
   text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
   text = re.sub(r'</?p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
   text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)
   text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)

   # Strip remaining HTML tags
   text = re.sub(r'<[^>]+>', '', text)

   # Decode HTML entities
   text = html_module.unescape(text)

   # Clean up whitespace
   text = re.sub(r'\n{3,}', '\n\n', text)
   text = re.sub(r'[ \t]+\n', '\n', text)
   text = text.strip()

   print(text)
   PYEOF
   ```

   If `html2text` is available (check with `python3 -c "import html2text" 2>/dev/null`), prefer it over the regex approach for higher quality HTML-to-markdown conversion:
   ```python
   import html2text
   h = html2text.HTML2Text()
   h.ignore_links = False
   h.ignore_images = True
   h.body_width = 0
   print(h.handle(html_content))
   ```

4. **Clean up the body text** - Post-process the email body:
   - Remove email signature blocks (lines after `-- ` on its own line, or common patterns like "Sent from my iPhone")
   - Remove excessive quoted reply chains (lines starting with `>`) — keep only the first/top message
   - Remove trailing whitespace from lines
   - Collapse 3+ consecutive blank lines to 2
   - Trim leading/trailing whitespace from the entire body
   - Preserve any meaningful formatting (lists, paragraphs)

5. **Derive the output filename** - Use the email subject line to create a clean filename:
   - If the email has a parseable date: `YYYY-MM-DD - Subject Line.md` (e.g., `2024-11-15 - Winter Camping Announcement.md`)
   - If no parseable date: use the original `.eml` filename with `.md` extension
   - Sanitize the subject line for use as a filename: remove characters not allowed in filenames (`< > : " / \ | ? *`), trim excessive whitespace, truncate to 80 characters max (before the `.md` extension)

6. **Generate frontmatter** - Add YAML frontmatter to the top of the file following the specification below.

7. **Write the output** - Save the cleaned markdown (with frontmatter) to the same directory as the source `.eml` file, using the derived filename.

8. **Show the user the result** - Display the output file path and the frontmatter that was generated.

## Frontmatter Specification

Every generated markdown file MUST begin with a YAML frontmatter block. Generate the following fields:

```yaml
---
title: ""              # From the email Subject line (cleaned up)
description: ""        # Brief 1-2 sentence summary of the email content
source_file: ""        # Original .eml filename (e.g., "message.eml")
converted_date: ""     # Today's date in YYYY-MM-DD format
original_format: "eml"
author: ""             # Sender's name (extracted from the From header, name portion only)
tags: []               # 2-5 relevant lowercase tags derived from the content
category: ""           # Leave empty for emails in temporary/staging folders (e.g., _organize, _convert, _inbox). Set to the parent directory name only when the file is in its final destination folder.
draft: false
email_from: ""         # Full From header value (e.g., "John Smith <john@example.com>")
email_to: ""           # Full To header value
email_cc: ""           # Full CC header value (omit field entirely if empty)
email_date: ""         # Date and time the email was sent in YYYY-MM-DD HH:MM format (24-hour, local time from the email)
email_subject: ""      # Original subject line, unmodified
email_account: ""      # Optional: the email account these were exported from (omit if --account not provided)
---
```

### Auto-Detection Rules

- **title**: Use the email Subject line. Remove common prefixes like `Re:`, `Fwd:`, `FW:` (and their nested/repeated forms) to get the clean topic. If the subject is empty, use `"(No Subject)"`.
- **description**: Generate a concise 1-2 sentence summary of the email's purpose and content based on the body text.
- **author**: Extract just the display name from the From header. For example, `"John Smith <john@example.com>"` → `"John Smith"`. If no display name, use the email address portion before `@`. If nothing is parseable, use `"Unknown"`.
- **tags**: Analyze the email content and assign 2-5 descriptive lowercase tags focused on subject matter (e.g., `["winter camping", "parent communication", "logistics"]`).
- **category**: Leave empty (`""`) if the output file is in a temporary/staging folder (any folder starting with `_`, such as `_organize`, `_convert`, `_inbox`). Otherwise, use the immediate parent directory name of the output file.
- **email_from**: Full From header value as-is.
- **email_to**: Full To header value as-is. If multiple recipients, include all of them.
- **email_cc**: Full CC header value as-is. **Omit this field entirely** if the CC header is empty or absent.
- **email_date**: Parsed date and time in `YYYY-MM-DD HH:MM` format (24-hour clock, using the timezone from the email header). If the date cannot be parsed, use the raw Date header value.
- **email_subject**: The original, unmodified subject line (including any Re:/Fwd: prefixes).
- **email_account**: The email account these were exported/downloaded from. Only include this field if `--account <email>` was passed in the arguments. If `--account` was not provided, omit the field entirely.
- **source**: Only include this field if `--source <url>` was passed in the arguments. Set it to the provided URL. If `--source` was not provided, omit the `source` field entirely.
- **last_downloaded**: Only include this field if `--source <url>` was passed in the arguments. Set it to today's date in YYYY-MM-DD format. If `--source` was not provided, omit this field entirely.

## Markdown Body Format

Structure the converted email body as follows:

```markdown
---
(frontmatter)
---

| | |
|---|---|
| **From** | John Smith <john@example.com> |
| **To** | Pack 232 Families <families@pack232.org> |
| **Date** | November 15, 2024 at 3:45 PM |

---

(email body content as clean markdown)

---

**Attachments:** filename1.pdf, filename2.docx
```

Rules for the body section:
- Start with a metadata table showing From, To, CC (if present), and Date using the human-readable display format.
- Add a horizontal rule (`---`) after the metadata table.
- Then the cleaned email body content.
- If attachments were present, list them at the bottom after another horizontal rule. If no attachments, omit this section entirely.
- Do NOT include the Subject in the body — it is already captured in the frontmatter `title`.

## Output Quality Standards

- Clean, readable markdown that renders well on GitHub
- Frontmatter must be valid YAML — use double quotes around values that contain colons, special characters, or could be misinterpreted
- Email body should read naturally as a standalone document
- No raw HTML artifacts in the output
- No excessive escape characters
- Quoted reply chains should be removed — only the primary message content is kept
