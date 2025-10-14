import argparse
import fnmatch
import os
import logging
import nbformat
from ps_core.ignore import parse_ignore_files as core_parse_ignore_files, collect_file_paths as core_collect_file_paths
from ps_core.tokens import get_all_content_counts
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)

IGNORE_FILES = [".gitignore", ".dockerignore"]


def parse_ignore_files(directory):
    return core_parse_ignore_files(directory)


def should_ignore(file_path, top_level_dir, ignore_patterns):
    # Kept for backward compatibility if imported elsewhere
    from ps_core.ignore import should_ignore as core_should_ignore
    return core_should_ignore(file_path, top_level_dir, ignore_patterns)


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
    return core_collect_file_paths(directory, global_ignore_patterns, include_ignore_files=True)


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
    if token_models:
        counts = get_all_content_counts(content, token_models)
        for m in token_models:
            if m in counts:
                total_token_counts[m] = counts[m]

    # Step 3: Log the aggregated results
    logging.info(f"Total Character Count: {total_character_count}")
    for model, token_count in total_token_counts.items():
        logging.info(f"Total Token Count ({model}): {token_count}")


def get_all_content_counts(content: str, models: list) -> dict:
    # Backward compatibility shim; delegate to core implementation
    from ps_core.tokens import get_all_content_counts as core_get_all_content_counts
    return core_get_all_content_counts(content, models)


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
