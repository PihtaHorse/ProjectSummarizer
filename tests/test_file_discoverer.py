"""Unit tests for FileDiscoverer."""

from projectsummarizer.files.discovery import FileDiscoverer


class TestFileDiscoverer:
    """Test class for FileDiscoverer functionality."""
    
    def test_gitignore_patterns_are_respected(self, test_project_dir, gitignore_fixture):
        """Test that FileDiscoverer correctly ignores files matching .gitignore patterns."""
        # Create .gitignore dynamically - ignore file_1.txt and folder_1/*
        with gitignore_fixture([
            "file_1.txt",
            "folder_1/*"
        ]):
            # Create discoverer with read_ignore_files=True (default)
            discoverer = FileDiscoverer(
                root=str(test_project_dir),
                read_ignore_files=True,
                use_defaults=False  # Don't use default patterns for this test
            )
            
            # Discover files
            files_data = discoverer.discover()
            
            # Verify that ignored files are not in the results
            assert "file_1.txt" not in files_data, "file_1.txt should be ignored"
            assert "folder_1/file_3.txt" not in files_data, "folder_1/file_3.txt should be ignored"
            
            # Verify that non-ignored files are still discovered
            assert "file_2.txt" in files_data, "file_2.txt should be discovered"
            assert "folder_2/file_4.txt" in files_data, "folder_2/file_4.txt should be discovered"
            assert "README.md" in files_data, "README.md should be discovered"
            
            # Verify discovered files have expected structure
            assert files_data["file_2.txt"]["size"] > 0
            assert "is_binary" in files_data["file_2.txt"]
    
    def test_user_patterns_can_ignore_files(self, test_project_dir, gitignore_fixture):
        """Test that user patterns can ignore files even if not in .gitignore."""
        # Create .gitignore with some patterns, but not file_2.txt
        with gitignore_fixture([
            "file_1.txt"
        ]):
            # Create discoverer with user patterns that ignore file_2.txt
            discoverer = FileDiscoverer(
                root=str(test_project_dir),
                user_patterns=["file_2.txt"],
                read_ignore_files=True,
                use_defaults=False
            )
            
            # Discover files
            files_data = discoverer.discover()
            
            # Verify that files ignored by .gitignore are not in results
            assert "file_1.txt" not in files_data, "file_1.txt should be ignored by .gitignore"
            
            # Verify that files ignored by user patterns are not in results
            assert "file_2.txt" not in files_data, "file_2.txt should be ignored by user pattern"
            
            # Verify that non-ignored files are still discovered
            assert "folder_1/file_3.txt" in files_data, "folder_1/file_3.txt should be discovered"
            assert "folder_2/file_4.txt" in files_data, "folder_2/file_4.txt should be discovered"
            assert "README.md" in files_data, "README.md should be discovered"
    
    def test_negation_pattern_overrides_gitignore(self, test_project_dir, gitignore_fixture):
        """Test that '!' user pattern can override .gitignore patterns."""
        # Create .gitignore that ignores file_1.txt
        with gitignore_fixture([
            "file_1.txt"
        ]):
            # Create discoverer with negation pattern to override .gitignore
            discoverer = FileDiscoverer(
                root=str(test_project_dir),
                user_patterns=["!file_1.txt"],  # Negation pattern to override .gitignore
                read_ignore_files=True,
                use_defaults=False
            )
            
            # Discover files
            files_data = discoverer.discover()
            
            # Verify that file_1.txt is now included despite being in .gitignore
            assert "file_1.txt" in files_data, "file_1.txt should be included due to negation pattern"
            
            # Verify other files are still discovered
            assert "file_2.txt" in files_data, "file_2.txt should be discovered"
            assert "folder_1/file_3.txt" in files_data, "folder_1/file_3.txt should be discovered"
            assert "folder_2/file_4.txt" in files_data, "folder_2/file_4.txt should be discovered"
            assert "README.md" in files_data, "README.md should be discovered"

