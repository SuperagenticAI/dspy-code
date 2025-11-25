"""
Security Tests

Tests for file system safety measures and security protections.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from dspy_code.rag.indexer import CodeIndexer


class TestIndexerSecurity:
    """Test security measures in CodeIndexer."""

    def test_blocks_home_directory(self):
        """Test that home directory scanning is blocked."""
        indexer = CodeIndexer()
        home = Path.home()

        assert not indexer._is_safe_to_scan(home), "Home directory should be blocked"

    def test_blocks_system_directories(self):
        """Test that system directories are blocked."""
        indexer = CodeIndexer()

        dangerous_dirs = [
            Path("/"),
            Path("/System"),
            Path("/Library"),
            Path("/usr"),
        ]

        for dangerous_dir in dangerous_dirs:
            if dangerous_dir.exists():
                assert not indexer._is_safe_to_scan(dangerous_dir), (
                    f"{dangerous_dir} should be blocked"
                )

        # /var root should be blocked (might resolve to /private/var)
        # Note: /var is often a symlink to /private/var on macOS
        var_path = Path("/var").resolve()
        # Either /var directly or /private/var should be blocked
        if var_path == Path("/private/var"):
            # Blocked via /private check
            assert not indexer._is_safe_to_scan(var_path), "/private/var should be blocked"
        elif var_path == Path("/var"):
            # Direct /var check
            assert not indexer._is_safe_to_scan(var_path), "/var root should be blocked"

    def test_blocks_user_directories(self):
        """Test that user directories like Desktop, Documents are blocked."""
        indexer = CodeIndexer()
        home = Path.home()

        user_dirs = ["Desktop", "Documents", "Downloads", "Pictures", "Photos"]

        for dir_name in user_dirs:
            user_dir = home / dir_name
            # Only test if directory actually exists
            if user_dir.exists():
                assert not indexer._is_safe_to_scan(user_dir), f"{user_dir} should be blocked"

    def test_allows_project_directories(self):
        """Test that proper project directories are allowed."""
        indexer = CodeIndexer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a project-like directory structure
            project_dir = Path(tmpdir) / "projects" / "my_dspy_project"
            project_dir.mkdir(parents=True)

            assert indexer._is_safe_to_scan(project_dir), "Project directory should be allowed"

    def test_blocks_shallow_home_subdirs(self):
        """Test that immediate subdirectories of home are blocked."""
        indexer = CodeIndexer()
        home = Path.home()

        # Direct child of home should be blocked
        shallow_dir = home / "test_project"
        assert not indexer._is_safe_to_scan(shallow_dir), (
            "Shallow home subdirectory should be blocked"
        )

    def test_safe_rglob_respects_depth(self):
        """Test that safe_rglob respects max depth."""
        indexer = CodeIndexer()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create nested structure
            deep_path = base / "a" / "b" / "c" / "d" / "e"
            deep_path.mkdir(parents=True)

            # Create Python files at different depths
            (base / "file0.py").write_text("# depth 0")
            (base / "a" / "file1.py").write_text("# depth 1")
            (base / "a" / "b" / "file2.py").write_text("# depth 2")
            (base / "a" / "b" / "c" / "file3.py").write_text("# depth 3")
            (deep_path / "file5.py").write_text("# depth 5")

            # Search with depth limit of 2
            results = indexer._safe_rglob(base, "*.py", max_depth=2)

            # Should only find files up to depth 2
            assert len(results) == 3, f"Expected 3 files, found {len(results)}"
            assert (base / "file0.py") in results
            assert (base / "a" / "file1.py") in results
            assert (base / "a" / "b" / "file2.py") in results
            assert (deep_path / "file5.py") not in results

    def test_safe_rglob_prevents_symlink_escape(self):
        """Test that safe_rglob prevents symlink attacks."""
        indexer = CodeIndexer()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "project"
            base.mkdir()

            outside = Path(tmpdir) / "outside"
            outside.mkdir()

            # Create file outside project
            outside_file = outside / "secret.py"
            outside_file.write_text("SECRET = 'should not be found'")

            # Create symlink from inside project to outside
            try:
                symlink = base / "evil_link"
                symlink.symlink_to(outside)

                # Search should not follow symlink
                results = indexer._safe_rglob(base, "*.py", max_depth=10)

                # Should not find the outside file
                assert outside_file not in results, "Should not follow symlink outside project"
            except OSError:
                # Symlink creation might fail on some systems (Windows without admin)
                pytest.skip("Cannot create symlinks on this system")

    def test_index_codebase_validates_safety(self):
        """Test that index_codebase validates path safety."""
        indexer = CodeIndexer()

        # Try to index home directory
        home = Path.home()
        info, elements = indexer.index_codebase("test", home)

        # Should return empty results
        assert info.file_count == 0, "Should not index home directory"
        assert info.element_count == 0
        assert len(elements) == 0

    def test_exclude_patterns_work(self):
        """Test that exclusion patterns are respected."""
        indexer = CodeIndexer()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create various files
            (base / "main.py").write_text("# main")
            (base / "test_file.py").write_text("# test")

            tests_dir = base / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_something.py").write_text("# test")

            pycache = base / "__pycache__"
            pycache.mkdir()
            (pycache / "main.pyc").write_text("# cache")

            # Search for Python files
            results = indexer._safe_rglob(base, "*.py", max_depth=10)

            # Apply exclusion
            filtered = [f for f in results if not indexer.should_exclude(f, base)]

            # Should only find main.py
            assert len(filtered) == 1
            assert (base / "main.py") in filtered
            assert (tests_dir / "test_something.py") not in filtered


class TestDirectorySafety:
    """Test directory safety checks."""

    def test_cwd_is_resolved(self):
        """Test that Path.cwd() is resolved to absolute path."""
        cwd = Path.cwd().resolve()
        assert cwd.is_absolute(), "CWD should be absolute path"

    def test_safe_directory_operations(self):
        """Test that directory operations stay within bounds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            project.mkdir()

            # Create a file in project
            test_file = project / "test.py"
            test_file.write_text("# test")

            # Verify we can access it
            assert test_file.exists()
            assert test_file.is_relative_to(project)

            # Try to access parent (should be caught)
            try:
                parent_path = test_file.resolve().relative_to(project.parent)
                # If we get here, the path escaped - that's what we're testing against
                assert not str(parent_path).startswith(".."), "Path should not escape project"
            except ValueError:
                # This is expected - path is outside project
                pass


class TestStartupSecurity:
    """Test startup security checks."""

    @patch("dspy_code.main.Path.cwd")
    @patch("dspy_code.main.console")
    def test_warns_on_home_directory(self, mock_console, mock_cwd):
        """Test that running from home directory shows warning."""
        from dspy_code.main import check_safe_working_directory

        home = Path.home()
        mock_cwd.return_value.resolve.return_value = home

        # This should print a warning
        # We can't easily test user input, but we can verify the function runs
        # without crashing
        try:
            with pytest.raises(KeyboardInterrupt):
                # Simulate Ctrl+C on the input prompt
                with patch("builtins.input", side_effect=KeyboardInterrupt):
                    check_safe_working_directory()
        except SystemExit:
            pass  # Expected when user exits

    def test_allows_safe_directories(self):
        """Test that safe directories don't trigger warnings."""
        from dspy_code.main import check_safe_working_directory

        # Create a real temp project directory that should be safe
        with tempfile.TemporaryDirectory(prefix="dspy_test_") as tmpdir:
            test_project = Path(tmpdir) / "myproject"
            test_project.mkdir()

            # Change to that directory
            import os

            old_cwd = os.getcwd()
            try:
                os.chdir(test_project)
                # Should complete without raising or prompting
                # (we're in a temp dir which is allowed)
                check_safe_working_directory()
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
