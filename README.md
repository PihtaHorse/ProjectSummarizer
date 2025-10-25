# ProjectSummarizer

A local alternative to [gitingest](https://gitingest.com/) that consolidates project structure and contents into a single file for LLM analysis.

## Why ProjectSummarizer?

While gitingest is a great web service, ProjectSummarizer runs entirely on your machine, giving you:
- Full control. No uploading to external servers, unless you want to.
- Token counting for multiple LLM models (OpenAI, Anthrophic, Google)
- Advanced filtering and ignore patterns

Perfect for feeding codebases to LLM platforms like [Claude Projects](https://claude.ai/projects) or [ChatGPT Projects](https://chatgpt.com).

## Installation

Using Poetry (recommended):
```bash
poetry install
```

## Example Output

Running:
```bash
poetry run python scripts/summarize.py --directory ./src/projectsummarizer/plotting/
```

Produces `summary.txt`:
```
Project Structure:
'''
.
├── __init__.py
└── tree_plotter.py
'''

## tree_plotter.py

'''
"""Tree plotting and ASCII visualization."""

from typing import List
from projectsummarizer.files.tree.node import FileSystemNode


class TreePlotter:
    """Plots filesystem trees in various formats."""

    @staticmethod
    def format_size(bytes_value: int) -> str:
        """Convert bytes to human-readable format.
        
        And the rest of the code... 
'''

## __init__.py

'''
"""Tree plotting and visualization utilities."""

from projectsummarizer.plotting.tree_plotter import TreePlotter

__all__ = [
    "TreePlotter",
]

'''
```

## Scripts

### [summarize.py](docs/summarize.md)
Main script that generates consolidated project summaries with optional token counting.

### [show_tree.py](docs/show_tree.md)
Displays project structure as an ASCII tree with file sizes and statistics. Usefull for trimming project.

### [simple_stats.py](docs/simple_stats.md)
Shows file extension statistics and helps generate ignore patterns. Can give some insights on what you've blocked.
