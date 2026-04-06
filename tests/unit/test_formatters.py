"""Unit tests for output formatters."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from projectsummarizer.contents.formatters import (
    create_formatter,
    BaseFormatter,
    StreamingTextFormatter,
    XMLFormatter,
    MarkdownFormatter,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def output_file(tmp_path):
    """Provide a temporary output file path."""
    return tmp_path / "output.txt"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestCreateFormatter:
    def test_text_format_returns_streaming_text_formatter(self, output_file):
        fmt = create_formatter("text", str(output_file))
        assert isinstance(fmt, StreamingTextFormatter)

    def test_xml_format_returns_xml_formatter(self, output_file):
        fmt = create_formatter("xml", str(output_file))
        assert isinstance(fmt, XMLFormatter)

    def test_markdown_format_returns_markdown_formatter(self, output_file):
        fmt = create_formatter("markdown", str(output_file))
        assert isinstance(fmt, MarkdownFormatter)

    def test_all_formatters_are_base_formatter_instances(self, output_file, tmp_path):
        for fmt_type in ("text", "xml", "markdown"):
            fmt = create_formatter(fmt_type, str(tmp_path / f"out_{fmt_type}.txt"))
            assert isinstance(fmt, BaseFormatter)


# ---------------------------------------------------------------------------
# StreamingTextFormatter
# ---------------------------------------------------------------------------

class TestStreamingTextFormatter:
    def test_context_manager_creates_file(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "print('hello')")
        assert output_file.exists()

    def test_write_content_increments_file_count(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_content("b.py", "y = 2")
        assert fmt.file_count == 2

    def test_write_content_skips_empty_content(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "")
        assert fmt.file_count == 0

    def test_output_contains_file_path_header(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("src/engine.py", "pass")
        content = output_file.read_text()
        assert "## src/engine.py" in content

    def test_output_contains_delimiter_blocks(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
        content = output_file.read_text()
        assert "```" in content

    def test_delimiter_in_content_is_replaced(self, output_file):
        fmt = StreamingTextFormatter(str(output_file), delimiter="```", delimiter_replacement="'''")
        with fmt:
            fmt.write_content("a.py", "code with ``` backticks")
        content = output_file.read_text()
        assert "'''" in content
        # The raw delimiter should not appear inside the content block
        lines = content.splitlines()
        # Find content between the first and last delimiter lines
        delim_indices = [i for i, l in enumerate(lines) if l == "```"]
        assert len(delim_indices) >= 2
        inner = "\n".join(lines[delim_indices[0] + 1:delim_indices[1]])
        assert "```" not in inner

    def test_write_tree_prepends_structure(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_tree(".\n└── a.py")
        content = output_file.read_text()
        assert content.startswith("Project Structure:")
        assert "## a.py" in content

    def test_write_tree_raises_when_file_not_open(self, output_file):
        fmt = StreamingTextFormatter(str(output_file))
        with pytest.raises(RuntimeError):
            fmt.write_tree("tree")

    def test_metadata_dates_are_written(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1", metadata={"created": "2024-01-01", "modified": "2024-06-01"})
        content = output_file.read_text()
        assert "created: 2024-01-01" in content
        assert "modified: 2024-06-01" in content

    def test_metadata_block_omitted_when_no_dates(self, output_file):
        with StreamingTextFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1", metadata={"size": 100})
        content = output_file.read_text()
        assert "---" not in content


# ---------------------------------------------------------------------------
# XMLFormatter
# ---------------------------------------------------------------------------

class TestXMLFormatter:
    def test_output_is_valid_xml(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("src/a.py", "x = 1")
            fmt.write_tree(".\n└── a.py")
        ET.parse(str(output_file))  # raises if invalid

    def test_output_has_documents_root(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_tree("tree")
        root = ET.parse(str(output_file)).getroot()
        assert root.tag == "documents"

    def test_document_element_has_correct_index(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_content("b.py", "y = 2")
            fmt.write_tree("tree")
        root = ET.parse(str(output_file)).getroot()
        docs = root.findall("document")
        assert docs[0].get("index") == "1"
        assert docs[1].get("index") == "2"

    def test_source_element_contains_path(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("src/engine.py", "pass")
            fmt.write_tree("tree")
        root = ET.parse(str(output_file)).getroot()
        source = root.find("document/source")
        assert source.text == "src/engine.py"

    def test_structure_element_contains_tree(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_tree(".\n└── a.py")
        root = ET.parse(str(output_file)).getroot()
        structure = root.find("structure")
        assert structure is not None
        assert "└── a.py" in structure.text

    def test_cdata_closing_sequence_in_content_is_safe(self, output_file):
        """File containing ']]>' must not break the XML."""
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("tricky.xml", "some ]]> content here")
            fmt.write_tree("tree")
        ET.parse(str(output_file))  # must not raise

    def test_file_count_increments(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_content("b.py", "y = 2")
            fmt.write_tree("tree")
        assert fmt.file_count == 2

    def test_empty_content_is_skipped(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "")
            fmt.write_tree("tree")
        assert fmt.file_count == 0

    def test_metadata_dates_written_as_xml_elements(self, output_file):
        with XMLFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1", metadata={"created": "2024-01-01", "modified": "2024-06-01"})
            fmt.write_tree("tree")
        root = ET.parse(str(output_file)).getroot()
        assert root.find("document/metadata/created").text == "2024-01-01"
        assert root.find("document/metadata/modified").text == "2024-06-01"

    def test_write_tree_raises_when_file_not_open(self, output_file):
        fmt = XMLFormatter(str(output_file))
        with pytest.raises(RuntimeError):
            fmt.write_tree("tree")


# ---------------------------------------------------------------------------
# MarkdownFormatter
# ---------------------------------------------------------------------------

class TestMarkdownFormatter:
    def test_context_manager_creates_file(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_tree("tree")
        assert output_file.exists()

    def test_output_contains_file_path_header(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("src/engine.py", "pass")
            fmt.write_tree("tree")
        content = output_file.read_text()
        assert "## src/engine.py" in content

    def test_output_contains_fenced_code_block(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_tree("tree")
        content = output_file.read_text()
        assert "```py" in content or "```python" in content or "```\n" in content

    def test_language_hint_inferred_from_extension(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("app.py", "pass")
            fmt.write_content("style.css", "body {}")
            fmt.write_tree("tree")
        content = output_file.read_text()
        assert "```py" in content
        assert "```css" in content

    def test_write_tree_prepends_h1_section(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_tree(".\n└── a.py")
        content = output_file.read_text()
        assert content.startswith("# Project Structure")
        assert "└── a.py" in content

    def test_file_count_increments(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1")
            fmt.write_content("b.py", "y = 2")
            fmt.write_tree("tree")
        assert fmt.file_count == 2

    def test_empty_content_is_skipped(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "")
            fmt.write_tree("tree")
        assert fmt.file_count == 0

    def test_metadata_dates_written_as_frontmatter(self, output_file):
        with MarkdownFormatter(str(output_file)) as fmt:
            fmt.write_content("a.py", "x = 1", metadata={"created": "2024-01-01", "modified": "2024-06-01"})
            fmt.write_tree("tree")
        content = output_file.read_text()
        assert "created: 2024-01-01" in content
        assert "modified: 2024-06-01" in content

    def test_write_tree_raises_when_file_not_open(self, output_file):
        fmt = MarkdownFormatter(str(output_file))
        with pytest.raises(RuntimeError):
            fmt.write_tree("tree")
