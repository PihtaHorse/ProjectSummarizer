import argparse
import fnmatch
import os
import logging
import nbformat

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


def process_directory(directory, ignore_patterns, outfile, special_character, only_structure=False):
    file_paths = collect_file_paths(directory, ignore_patterns)
    # Write the project structure at the beginning
    outfile.write(f"Files:\n{special_character}\n")
    for relative_path in file_paths:
        outfile.write(f" {relative_path}\n")
    outfile.write(f"{special_character}\n\n")  # Extra newline for separation

    if only_structure:
        return

    # Append file contents
    for relative_path in file_paths:
        file_path = os.path.join(directory, relative_path)
        logging.info(f"Processing {file_path}")
        if file_path.endswith('.ipynb'):
            content = extract_notebook_content(file_path)
        else:
            with open(file_path, "r", encoding='utf-8') as infile:
                content = infile.read()
        write_file_content(outfile, relative_path, special_character, content)


def summarize_project(directory, special_character, output_file, global_ignore_patterns, only_structure=False):
    global_ignore_patterns = list(global_ignore_patterns) + parse_ignore_files(directory)
    with open(output_file, "w", encoding='utf-8') as outfile:
        process_directory(directory, global_ignore_patterns, outfile, special_character, only_structure=only_structure)

    # Count the number of characters in the output file
    with open(output_file, "r", encoding='utf-8') as outfile:
        content = outfile.read()
        logging.info(f"Total number of characters in the summarized document: {len(content)}")


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
    args = parser.parse_args()

    summarize_project(
        args.directory, 
        args.special_character, 
        args.output_file, 
        args.ignore_patterns.split(","), 
        only_structure=args.only_structure
    )
