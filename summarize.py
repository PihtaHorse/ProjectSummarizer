import argparse
import fnmatch
import os
import logging
import nbformat
from token_handlers.openai_token_handler import get_openai_token_count
from token_handlers.anthropic_token_handler import get_anthropic_token_count
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)

IGNORE_FILES = [".gitignore", ".dockerignore"]


def parse_ignore_files(directory):
    ignore_patterns = []
    for ignore_file in IGNORE_FILES:
        ignore_path = os.path.join(directory, ignore_file)
        if os.path.exists(ignore_path):
            with open(ignore_path, "r", encoding='utf-8') as file:
                ignore_patterns.extend(
                    line.strip() for line in file if line.strip() and not line.startswith("#")
                )
    return ignore_patterns


def should_ignore(file_path, top_level_dir, ignore_patterns):
    # Always compute relative paths from the top-level directory
    relative_path = os.path.relpath(file_path, top_level_dir).replace(os.sep, "/")
    for pattern in ignore_patterns:
        if fnmatch.fnmatchcase(relative_path, pattern):
            return True
    return False


def write_file_content(outfile, name, special_character, content):
    outfile.write(f"{name}:\n")
    outfile.write(f"{special_character}\n")
    outfile.write(content)
    outfile.write(f"\n{special_character}\n\n")


def extract_notebook_content(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    content = ""
    for cell in nb.cells:
        if cell.cell_type in ['code', 'markdown']:
            if cell.source:
                content += f"# {cell.cell_type.capitalize()} cell\n{cell.source}\n\n"
    return content


def collect_file_paths(directory, global_ignore_patterns):
    file_paths = []
    # Pre-parse ignore files from the top-level directory
    top_level_ignore_patterns = global_ignore_patterns + parse_ignore_files(directory)

    for root, dirs, files in os.walk(directory, topdown=True):
        # Combine top-level patterns with local ignore files from the current root
        local_ignore_patterns = top_level_ignore_patterns + parse_ignore_files(root)
        # Filter directories
        dirs[:] = [
            d for d in dirs if not should_ignore(os.path.join(root, d), directory, local_ignore_patterns)
        ]
        # Filter files
        for name in files:
            file_path = os.path.join(root, name)
            if not should_ignore(file_path, directory, local_ignore_patterns):
                rel_path = os.path.relpath(file_path, directory).replace(os.sep, "/")
                file_paths.append(rel_path)
    return file_paths


def process_directory(directory, ignore_patterns, outfile, special_character, only_structure=False, max_file_size=5 * 1024 * 1024):
    # Collect file paths
    file_paths = collect_file_paths(directory, ignore_patterns)

    # Write the project structure
    outfile.write(f"Files:\n{special_character}\n")
    for relative_path in file_paths:
        outfile.write(f" {relative_path}\n")
    outfile.write(f"{special_character}\n\n")

    if only_structure:
        logging.info("Only structure output is enabled. Skipping file content processing.")
        return

    # Process and write file contents
    for relative_path in file_paths:
        file_path = os.path.join(directory, relative_path)
        file_size = os.path.getsize(file_path)

        if file_size > max_file_size:
            logging.warning(f"Skipping {file_path}: file size exceeds {max_file_size} bytes")
            continue

        logging.info(f"Processing {file_path}")
        if file_path.endswith('.ipynb'):
            content = extract_notebook_content(file_path)
        else:
            with open(file_path, "r", encoding='utf-8') as infile:
                content = infile.read()

        # Write the file content to the output file
        write_file_content(outfile, relative_path, special_character, content)


def summarize_project(directory, special_character, output_file, global_ignore_patterns, only_structure=False, max_file_size=5 * 1024 * 1024, token_models=None):
    if token_models is None:
        token_models = []

    # Step 1: Write project structure and contents to output file
    global_ignore_patterns = list(global_ignore_patterns) + parse_ignore_files(directory)
    with open(output_file, "w", encoding='utf-8') as outfile:
        process_directory(directory, global_ignore_patterns, outfile, special_character, only_structure=only_structure, max_file_size=max_file_size)

    # Step 2: Perform final counts on the entire output file
    with open(output_file, "r", encoding='utf-8') as outfile:
        content = outfile.read()

    # Count characters
    total_character_count = len(content)

    # Count tokens for each model
    total_token_counts = {}
    for model in token_models:
        if model == "gpt-4o":
            total_token_counts["gpt-4o"] = get_openai_token_count(content, "gpt-4o")
        elif model == "claude-3-5-sonnet-20241022":
            total_token_counts["claude-3-5-sonnet-20241022"] = get_anthropic_token_count(
                [{"role": "user", "content": content}], "claude-3-5-sonnet-20241022"
            )

    # Step 3: Log the aggregated results
    logging.info(f"Total Character Count: {total_character_count}")
    for model, token_count in total_token_counts.items():
        logging.info(f"Total Token Count ({model}): {token_count}")


def get_all_content_counts(content: str, models: list) -> dict:
    """
    Calculates character count and token counts for specified models.

    Args:
        content: The input text content.
        models: A list of model names for which token counts should be calculated.

    Returns:
        A dictionary with character count and token counts.
    """
    counts = {"characters": len(content)}

    if "gpt-4o" in models:
        counts["gpt-4o"] = get_openai_token_count(content, "gpt-4o")

    if "claude-3-5-sonnet-20241022" in models:
        counts["claude-3-5-sonnet-20241022"] = get_anthropic_token_count(
            [{"role": "user", "content": content}], "claude-3-5-sonnet-20241022"
        )

    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Summarize project files, optionally including their contents."
    )
    parser.add_argument(
        "--directory", type=str, required=True, help="Directory path containing the files"
    )
    parser.add_argument(
        "--special_character",
        type=str,
        required=False,
        default="```",
        help="Special character to use as a delimiter for file content",
    )
    parser.add_argument(
        "--output_file", type=str, default="summary.txt", required=False, help="Output file to write the contents"
    )
    parser.add_argument(
        "--ignore_patterns",
        type=str,
        default=".git,*.gitignore,*.dockerignore,*.png,*.jpg",
        help="Comma-separated list of patterns to ignore",
    )
    parser.add_argument(
        "--only_structure",
        action="store_true",
        help="If set, only output the project structure without file contents"
    )

    parser.add_argument(
        "--max_file_size",
        type=int,
        default=5 * 1024 * 1024,
        help="Maximum file size (in bytes) to include in the summary. Default is 5 MB."
    )

    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify one or more models to count tokens for (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')."
    )
    
    args = parser.parse_args()

    summarize_project(
        args.directory, 
        args.special_character, 
        args.output_file, 
        args.ignore_patterns.split(","), 
        only_structure=args.only_structure,
        max_file_size=args.max_file_size,
        token_models=args.count_tokens or []
    )
