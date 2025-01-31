# ProjectSummarizer

ProjectSummarizer is a script that consolidates the structure and optionally the contents of a project directory into a single output file.

The tool integrates with popular LLM platforms that support project analysis:
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