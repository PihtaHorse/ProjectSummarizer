#!/usr/bin/env python3
"""Simple script to show active patterns and binary extensions."""

import argparse
import sys

from projectsummarizer.files.discovery.discoverer import FileScanner


def main():
    """Main entry point for simple stats script."""
    parser = argparse.ArgumentParser(
        description="Show active patterns and binary extensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --directory .
  %(prog)s --directory . --ignore_patterns "*.tmp,*.log"
        """
    )
    
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory to analyze (default: current directory)"
    )
    
    parser.add_argument(
        "--ignore_patterns",
        type=str,
        help="Additional ignore patterns (comma-separated)"
    )
    
    parser.add_argument(
        "--no_defaults",
        action="store_true",
        help="Don't use default ignore patterns"
    )
    
    parser.add_argument(
        "--no_gitignore",
        action="store_true",
        help="Don't read .gitignore files"
    )
    
    args = parser.parse_args()
    
    # Parse additional patterns
    user_patterns = []
    if args.ignore_patterns:
        user_patterns.extend(args.ignore_patterns.split(","))
    
    # Create scanner with centralized ignore logic
    scanner = FileScanner(
        root=args.directory,
        user_patterns=user_patterns,
        use_defaults=not args.no_defaults,
        read_ignore_files=not args.no_gitignore,
        include_binary=True,  # We want to track binary files
    )
    
    try:
        # Run discovery to populate pattern tracker
        scanner.discover()
        
        # Get active patterns grouped by origin
        patterns_by_origin = scanner.ignore_handler.get_active_patterns_by_origin()
        
        # Get binary extensions
        binary_extensions = scanner.ignore_handler.get_binary_extensions()
        
        # Print results
        print("Active patterns (covering at least one file):")
        if patterns_by_origin:
            for origin, patterns in patterns_by_origin.items():
                if patterns:  # Only show non-empty groups
                    origin_name = {
                        "user": "User patterns", 
                        "default": "Default patterns",
                        "gitignore": ".gitignore patterns",
                        "unknown": "Unknown origin"
                    }.get(origin, origin.title())
                    
                    print(f"\n  {origin_name}:")
                    patterns_str = ",".join(f'{pattern}' for pattern in patterns)
                    print(f"     {patterns_str}")
        else:
            print("  None")
        
        # Only show binary extensions if there are any
        if binary_extensions:
            print("\n  Binary extensions that were blocked:")
            # Format as comma-separated string for easy copy-paste
            extensions_str = ",".join(f'*{ext}' for ext in binary_extensions)
            print(f"   {extensions_str}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
