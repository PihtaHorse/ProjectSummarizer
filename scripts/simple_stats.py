#!/usr/bin/env python3
"""Simple script to show active patterns and binary extensions."""

import argparse
import sys
from prettytable import PrettyTable

from projectsummarizer.files.discovery.discoverer import FileDiscoverer


def create_pattern_table(patterns_by_origin, pattern_matches):
    """Create a table showing patterns by origin and their file counts."""
    table = PrettyTable()
    table.field_names = ["Origin", "Pattern", "Files Affected"]
    table.align["Pattern"] = "l"
    table.align["Files Affected"] = "r"
    
    for origin, patterns in patterns_by_origin.items():
        for pattern in patterns:
            file_count = pattern_matches.get(pattern, 0)
            table.add_row([origin.title(), pattern, file_count])
    
    return table


def create_binary_extensions_table(binary_extensions, checked_files):
    """Create a table showing binary extensions and their file counts."""
    table = PrettyTable()
    table.field_names = ["Extension", "Files Affected", "Blocked Files"]
    table.align["Extension"] = "l"
    table.align["Files Affected"] = "r"
    table.align["Blocked Files"] = "r"
    
    for ext in binary_extensions:
        # Count total files with this extension
        total_files = sum(1 for data in checked_files.values() 
                         if data.get("binary_extension") == ext)
        
        # Count blocked files with this extension
        blocked_files = sum(1 for data in checked_files.values() 
                           if data.get("binary_extension") == ext and data.get("is_ignored", False))
        
        table.add_row([ext, total_files, blocked_files])
    
    return table


def create_ignore_summary_table(checked_files):
    """Create a summary table of ignore statistics."""
    table = PrettyTable()
    table.field_names = ["Category", "Count"]
    table.align["Category"] = "l"
    table.align["Count"] = "r"
    
    total_files = len(checked_files)
    ignored_files = sum(1 for data in checked_files.values() if data.get("is_ignored", False))
    binary_files = sum(1 for data in checked_files.values() if data.get("is_binary", False))
    binary_ignored = sum(1 for data in checked_files.values() 
                        if data.get("is_binary", False) and data.get("is_ignored", False))
    
    table.add_row(["Total files checked", total_files])
    table.add_row(["Files ignored", ignored_files])
    table.add_row(["Binary files found", binary_files])
    table.add_row(["Binary files blocked", binary_ignored])
    table.add_row(["Files included", total_files - ignored_files])
    
    return table


def create_ignored_files_table(checked_files, max_files=20):
    """Create a table showing detailed information about ignored files."""
    table = PrettyTable()
    table.field_names = ["File", "Reason", "Binary", "Patterns"]
    table.align["File"] = "l"
    table.align["Reason"] = "l"
    table.align["Binary"] = "c"
    table.align["Patterns"] = "l"
    
    ignored_files = [(path, data) for path, data in checked_files.items() 
                    if data.get("is_ignored", False)]
    
    # Sort by file path for consistent output
    ignored_files.sort(key=lambda x: x[0])
    
    # Limit to max_files for readability
    for path, data in ignored_files[:max_files]:
        reasons = []
        if data.get("is_binary", False):
            reasons.append("binary")
        if data.get("matched_patterns"):
            reasons.append("pattern")
        
        reason_str = ", ".join(reasons) if reasons else "unknown"
        binary_str = "✓" if data.get("is_binary", False) else "✗"
        patterns_str = ", ".join(data.get("matched_patterns", [])) or "-"
        
        table.add_row([path, reason_str, binary_str, patterns_str])
    
    if len(ignored_files) > max_files:
        table.add_row([f"... and {len(ignored_files) - max_files} more", "", "", ""])
    
    return table


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
    
    parser.add_argument(
        "--show_ignored_files",
        action="store_true",
        help="Show detailed list of ignored files"
    )
    
    parser.add_argument(
        "--include_binary",
        action="store_true",
        help="Include binary files (don't block them)"
    )
    
    args = parser.parse_args()
    
    # Parse additional patterns
    user_patterns = []
    if args.ignore_patterns:
        user_patterns.extend(args.ignore_patterns.split(","))
    
    # Create discoverer with centralized ignore logic
    discoverer = FileDiscoverer(
        root=args.directory,
        user_patterns=user_patterns,
        use_defaults=not args.no_defaults,
        read_ignore_files=not args.no_gitignore,
        include_binary=args.include_binary,  # Allow user to control binary file inclusion
    )

    try:
        # Run discovery to populate pattern tracker
        discoverer.discover()

        # Get data for tables
        patterns_by_origin = discoverer.ignore_handler.get_active_patterns_by_origin()
        binary_extensions = discoverer.ignore_handler.get_binary_extensions()
        pattern_matches = discoverer.ignore_handler._pattern_matches
        checked_files = discoverer.ignore_handler.get_checked_files_data()
        
        # Create and display tables
        print("📊 IGNORE PATTERNS ANALYSIS")
        print("=" * 50)
        
        # Summary table
        summary_table = create_ignore_summary_table(checked_files)
        print("\n📈 SUMMARY")
        print(summary_table)
        
        # Pattern details table
        if patterns_by_origin:
            pattern_table = create_pattern_table(patterns_by_origin, pattern_matches)
            print("\n🎯 ACTIVE PATTERNS")
            print(pattern_table)
        else:
            print("\n🎯 ACTIVE PATTERNS")
            print("No patterns matched any files.")
        
        # Binary extensions table
        if binary_extensions:
            binary_table = create_binary_extensions_table(binary_extensions, checked_files)
            print("\n🔒 BINARY FILE EXTENSIONS")
            print(binary_table)
        else:
            print("\n🔒 BINARY FILE EXTENSIONS")
            print("No binary files were found.")
        
        # Detailed ignored files table (if requested)
        if args.show_ignored_files:
            ignored_files = [f for f, data in checked_files.items() if data.get("is_ignored", False)]
            if ignored_files:
                ignored_table = create_ignored_files_table(checked_files)
                print("\n📋 IGNORED FILES DETAILS")
                print(ignored_table)
            else:
                print("\n📋 IGNORED FILES DETAILS")
                print("No files were ignored.")
        
        # String outputs for easy copy-paste
        print("\n" + "=" * 50)
        print("📋 COPY-PASTE STRINGS")
        print("=" * 50)
        
        # Active patterns strings
        if patterns_by_origin:
            print("\n🎯 Active patterns (covering at least one file):")
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
            print("\n🎯 Active patterns (covering at least one file):")
            print("  None")
        
        # Binary extensions strings
        if binary_extensions:
            print("\n🔒 Binary extensions that were blocked:")
            extensions_str = ",".join(f'*{ext}' for ext in binary_extensions)
            print(f"   {extensions_str}")
        else:
            print("\n🔒 Binary extensions that were blocked:")
            print("  None")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
