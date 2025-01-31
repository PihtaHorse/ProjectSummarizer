# ProjectSummarizer
ProjectSummarizer is a script that consolidates the structure and optionally the contents of a project directory into a single output file. It supports various ignore patterns, can parse .gitignore and .dockerignore files, and can handle Jupyter notebooks by extracting their code and markdown cells.

It can be useful for creating a summary of a project to provide your favorite LLM or projects feature from some LLM providers:
- [Claude projects](https://claude.ai/projects)
- projects tab in [ChatGPT](https://chatgpt.com)

## Features
- Recursively lists all files and directories, writing their paths to an output file.
- Optionally includes the contents of each file.
- Honors ignore patterns from .gitignore, .dockerignore, and user-specified patterns.
- Provides an option to output only the file structure without contents.
- Prints the total character count of the output.
- Configurable delimiter for file content sections.
- Works with jupyter notebooks (ignores output cells)


## Instalation
```sh
poetry install
```

## Usage
Run the script from the command line:

```sh
python summaraize.py
--directory <DIRECTORY>
--output_file <OUTPUT_FILE>
[--special_character <SPECIAL_CHAR>]
[--ignore_patterns <PATTERNS>]
[--only_structure] 
```

Arguments:

- directory (required): The path to the project directory to summarize.
- output_file (required): The file to write the project summary to.
- special_character (optional): The delimiter for file contents (default: ```).
- ignore_patterns (optional): Comma-separated list of patterns to ignore.
Defaults to: .git,*.gitignore,*.dockerignore,*.png,*.jpg
- only_structure (optional, flag): If provided, only the structure (list of files) is written, without file contents.
Examples
Summarize a project including file contents:

``` sh
python summaraize.py
--directory ./my_project
--output_file summary.txt 
```

This command will include all non-ignored files and their contents in summary.txt.

Summarize only the structure (no contents):

```sh 
python summaraize.py
--directory ./my_project
--output_file structure_only.txt
--only_structure 
```

This command will list all non-ignored files but will not include their contents.

Use a custom ignore patterns:

```sh 
python summaraize.py
--directory ./my_project
--ignore_patterns ".git,*.gitignore,*.dockerignore,*.png,*.jpg,*.json,folder/i/want/to/exclude/*" 
```

Exclude certain directories by pattern:

If you want to exclude all files in `experiments/` and `evaluation_results/` directories:

```sh
python summaraize.py --directory ./my_project --ignore_patterns "experiments/*,evaluation_results/*" 
```

This will ignore all files under `experiments` and `evaluation_results` directories.