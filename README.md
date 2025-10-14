# ProjectSummarizer

ProjectSummarizer is a script that consolidates the structure and optionally the contents of a project directory into a single output file.
Script alternative for [gitingest](https://gitingest.com/).

You can use the generated file with LLM platforms that support project analysis:
- [Claude projects](https://claude.ai/projects)
- [Projects tab in ChatGPT](https://chatgpt.com)

It's particularly useful for learning new tools by consolidating their documentation into a single file for LLM analysis. The tool also helps when working with codebases, allowing you to ask LLMs questions about either small projects or specific parts of larger ones.

## Example Output

Here's an example of what the tool produces for a simple project:

Command:
```
python summarize.py --directory ./my_project --output_file summary.txt --count_tokens gpt-4o claude-3-5-sonnet-20241022
```

Output in `summary.txt`:
```
Files:
'''
 src/
   main.py
 tests/
   test_main.py
'''

src/main.py:
'''
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
'''

tests/test_main.py:
'''
def test_hello_world():
    assert hello_world() == "Hello, World!"
'''
```

And in console you will see token counts:

```
Token Counts:
- GPT-4: 428 tokens
- Claude 3.5 Sonnet: 412 tokens
Characters: 1847
```

## Features
- Recursively lists all files and directories, writing their paths to an output file
- Optionally includes the contents of each file
- Honors ignore patterns from .gitignore, .dockerignore, and user-specified patterns
- Provides an option to output only the file structure without contents
- Supports token counting for various LLM models (Claude and GPT)
- Configurable delimiter for file content sections
- Works with jupyter notebooks (ignores output cells)

## Installation

This project uses poetry to manage dependencies. But you can use whatever you want, the list of dependencies is in `pyproject.toml`.

```sh
poetry install
```

## Usage

Run the script from the command line:

```sh
python summarize.py --directory <DIRECTORY> --output_file <OUTPUT_FILE> [--special_character <SPECIAL_CHAR>] [--ignore_patterns <PATTERNS>] [--only_structure] [--count_tokens gpt-4o claude-3-5-sonnet-20241022]
```

### Arguments

- **--directory** (required): The path to the project directory to summarize
- **--output_file** (optional): The file to write the project summary to
- **--special_character** (optional): The delimiter for file contents (default: ```)
- **--ignore_patterns** (optional): Comma-separated list of patterns to ignore (default: .git,*.gitignore,*.dockerignore,*.png,*.jpg)
- **--only_structure** (optional, flag): If provided, only the structure (list of files) is written, without file contents
- **--count_tokens** (optional): Specify models to count tokens for (supports gpt-4o and claude-3-5-sonnet-20241022). It is useful if you know models context window size. For example, GPT-4o has 128k tokens and Claude 3.5 Sonnet 200K token context window.
- **--max_file_size** (optional): Maximum file size in bytes to include in the summary (default: 5MB)

### Example Commands

Summarize a project including file contents and token counts:
```sh
python summarize.py --directory ./my_project --output_file summary.txt --count_tokens gpt-4o claude-3-5-sonnet-20241022
```

Summarize only the structure (no contents):
```sh
python summarize.py --directory ./my_project --output_file structure_only.txt --only_structure
```

Use custom ignore patterns:
```sh
python summarize.py --directory ./my_project --ignore_patterns ".git,*.gitignore,*.dockerignore,*.png,*.jpg,*.json,folder/to/exclude/*"
```

## Additional CLIs

Two helper CLIs are included to make exploration and ignore pattern generation faster.

### Tree view with totals: `tree_stats.py`

Prints folder tree and totals; optionally counts tokens across all included files.

```sh
python tree_stats.py --directory <DIRECTORY> [--ignore_patterns <PATTERNS>] [--count_tokens gpt-4o claude-3-5-sonnet-20241022]
```

Examples:

```sh
# Basic
python tree_stats.py --directory ./my_project

# With additional ignore patterns
python tree_stats.py --directory ./my_project --ignore_patterns ".git,*.png,*.jpg,*.pdf,**/__pycache__/*"

# With token counts (requires API keys in environment/.env)
python tree_stats.py --directory ./my_project --count_tokens gpt-4o claude-3-5-sonnet-20241022
```

### Extension stats and ignore helper: `ignore_helper.py`

Lists extensions and prints a copy-pasteable ignore pattern list. It outputs a tab-separated table: `extension`, `count`, `size`, and, if `--count_tokens` is provided, one column per model with total tokens for that extension.

```sh
python ignore_helper.py --directory <DIRECTORY> [--ignore_patterns <PATTERNS>] [--list_extensions all|effective|removed] [--count_tokens gpt-4o claude-3-5-sonnet-20241022]
```

Flags:
- `--list_extensions`: which set to show
  - `all`: all files (no ignore files or patterns applied)
  - `effective` (default): files after applying `.gitignore`, `.dockerignore`, and `--ignore_patterns`
  - `removed`: files/extensions excluded by the ignore rules

Examples:

```sh
# Effective extensions after ignores
python ignore_helper.py --directory ./my_project --list_extensions effective

# All extensions (raw view)
python ignore_helper.py --directory ./my_project --list_extensions all

# Removed extensions
python ignore_helper.py --directory ./my_project --list_extensions removed

# Include token counts per extension
python ignore_helper.py --directory ./my_project --list_extensions effective --count_tokens gpt-4o

# Provide extra patterns to refine the result; copy the printed pattern list for summarize.py
python ignore_helper.py --directory ./my_project --ignore_patterns ".git,*.png,*.jpg,*.pdf" --list_extensions effective
```

## Try it on this repository

Use these copy-pasteable commands to run against this repo:

```sh
# Tree view for this repo
python scripts/tree_stats.py --directory .

# Extension stats (effective) for this repo
python scripts/ignore_helper.py --directory . --list_extensions effective

# Summarize this repo (structure only)
python scripts/summarize.py --directory . --output_file ./summary.txt --only_structure

# Summarize with common ignores
python scripts/summarize.py --directory . --output_file ./summary.txt --ignore_patterns ".git,*.png,*.jpg,*.pdf,**/__pycache__/*"

# Optional: include token counts (requires keys in env/.env)
python scripts/tree_stats.py --directory . --count_tokens gpt-4o
```
