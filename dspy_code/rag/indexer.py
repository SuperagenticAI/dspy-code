"""
Code indexer for discovering and parsing source code from installed packages.

This module handles the discovery of installed packages, parsing Python files
with AST, extracting code elements, and caching the results.
"""

import ast
import gzip
import importlib
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from ..core.config import ConfigManager
from .models import CodebaseInfo, CodeElement, CodeIndex

logger = logging.getLogger(__name__)


class CodeIndexer:
    """Indexes source code from installed packages.

    This class discovers installed packages (dspy-cli, dspy, gepa, mcp),
    parses Python files using AST, extracts code elements, and caches
    the results for fast retrieval.
    """

    # Default exclusion patterns
    DEFAULT_EXCLUDE_PATTERNS = [
        "tests/",
        "test_*.py",
        "__pycache__/",
        "*.pyc",
        ".git/",
        ".venv/",
        "venv/",
        "build/",
        "dist/",
        "*.egg-info/",
        "node_modules/",
        "__pycache__",
        "experimental/",
        "examples/",
    ]

    # Index format version
    INDEX_VERSION = "1.0.0"

    def __init__(self, cache_dir: Path | None = None, config_manager: ConfigManager | None = None):
        """Initialize the code indexer.

        Args:
            cache_dir: Directory for caching index (defaults to ~/.dspy_cli/cache/codebase_index)
            config_manager: Configuration manager for reading settings
        """
        self.config_manager = config_manager

        # Set up cache directory
        if cache_dir is None:
            cache_dir = Path.home() / ".dspy_cli" / "cache" / "codebase_index"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load exclusion patterns from config or use defaults
        self.exclude_patterns = self._load_exclude_patterns()

        logger.info(f"CodeIndexer initialized with cache dir: {self.cache_dir}")

    def _load_exclude_patterns(self) -> list[str]:
        """Load exclusion patterns from config or use defaults."""
        if self.config_manager and hasattr(self.config_manager.config, "codebase_rag"):
            rag_config = self.config_manager.config.codebase_rag
            if hasattr(rag_config, "exclude_patterns") and rag_config.exclude_patterns:
                return rag_config.exclude_patterns
        return self.DEFAULT_EXCLUDE_PATTERNS.copy()

    def discover_codebases(self) -> dict[str, Path]:
        """Discover all available codebases dynamically.

        Indexes the user's INSTALLED packages (their DSPy version) and project code.
        This makes the CLI adapt to whatever DSPy version the user has installed.

        Handles permission issues gracefully - if we can't read a package directory,
        we skip it and continue with what we can access.

        Returns:
            Dictionary mapping codebase name to path
        """
        codebases = {}

        # 1. Index INSTALLED packages (user's actual DSPy/GEPA version)
        # This is the "living playbook" approach - use their installed version!
        for package_name in ["dspy", "gepa", "mcp"]:
            try:
                module = importlib.import_module(package_name)
                if hasattr(module, "__file__") and module.__file__:
                    package_path = Path(module.__file__).parent

                    # Check if we can actually read this directory
                    if not package_path.exists():
                        logger.warning(f"{package_name} path doesn't exist: {package_path}")
                        continue

                    if not os.access(package_path, os.R_OK):
                        logger.warning(f"No read permission for {package_name} at {package_path}")
                        logger.info(f"Skipping {package_name} - will work without it")
                        continue

                    # Try to list files to verify we can actually read it
                    try:
                        list(package_path.glob("*.py"))
                    except (PermissionError, OSError) as e:
                        logger.warning(f"Cannot read {package_name} directory: {e}")
                        logger.info(f"Skipping {package_name} - will work without it")
                        continue

                    codebases[package_name] = package_path

                    # Try to get version
                    version = "unknown"
                    try:
                        import importlib.metadata

                        version = importlib.metadata.version(package_name)
                    except:
                        pass

                    logger.info(
                        f"✓ Discovered installed {package_name} {version} at {package_path}"
                    )
            except ImportError:
                logger.debug(f"{package_name} not installed, skipping")
            except Exception as e:
                logger.warning(f"Error discovering {package_name}: {e}")
                logger.info(f"Skipping {package_name} - will work without it")

        # 2. Index user's project code (their DSPy programs)
        try:
            project_root = Path.cwd()

            # Check if we have read access to current directory
            if not os.access(project_root, os.R_OK):
                logger.warning(f"No read permission for current directory: {project_root}")
            else:
                # Look for common DSPy project directories
                for dir_name in [
                    "generated",
                    "modules",
                    "signatures",
                    "programs",
                    "optimizers",
                    "src",
                ]:
                    try:
                        project_code_dir = project_root / dir_name
                        if project_code_dir.exists() and project_code_dir.is_dir():
                            # Check read permission
                            if not os.access(project_code_dir, os.R_OK):
                                logger.debug(f"No read permission for {project_code_dir}")
                                continue

                            # Check if it has Python files
                            py_files = list(project_code_dir.glob("*.py"))
                            if py_files:
                                codebases[f"user_project_{dir_name}"] = project_code_dir
                                logger.info(
                                    f"✓ Discovered user project code at {project_code_dir} ({len(py_files)} files)"
                                )
                    except (PermissionError, OSError) as e:
                        logger.debug(f"Cannot access {dir_name}: {e}")
                        continue

                # Also check root directory for Python files (but exclude common non-project files)
                try:
                    root_py_files = [
                        f
                        for f in project_root.glob("*.py")
                        if f.name not in ["setup.py", "conftest.py"]
                        and not f.name.startswith("test_")
                    ]
                    if root_py_files:
                        codebases["user_project_root"] = project_root
                        logger.info(
                            f"✓ Discovered user project root at {project_root} ({len(root_py_files)} files)"
                        )
                except (PermissionError, OSError) as e:
                    logger.debug(f"Cannot scan root directory: {e}")
        except Exception as e:
            logger.warning(f"Error scanning project code: {e}")

        # 3. Discover MCP servers from config
        if self.config_manager:
            try:
                mcp_servers = getattr(self.config_manager.config, "mcp_servers", {})
                if mcp_servers:
                    for server_name, server_config in mcp_servers.items():
                        try:
                            if isinstance(server_config, dict) and "path" in server_config:
                                server_path = Path(server_config["path"])
                                if server_path.exists() and server_path.is_dir():
                                    # Check read permission
                                    if not os.access(server_path, os.R_OK):
                                        logger.warning(
                                            f"No read permission for MCP server {server_name} at {server_path}"
                                        )
                                        continue

                                    codebases[f"mcp_{server_name}"] = server_path
                                    logger.info(
                                        f"✓ Discovered MCP server {server_name} at {server_path}"
                                    )
                        except (PermissionError, OSError) as e:
                            logger.warning(f"Cannot access MCP server {server_name}: {e}")
                            continue
            except Exception as e:
                logger.warning(f"Error discovering MCP servers: {e}")

        if not codebases:
            logger.warning("⚠️  No codebases discovered for indexing!")
            logger.warning("This can happen due to:")
            logger.warning("  • Permission issues accessing installed packages")
            logger.warning("  • No DSPy/GEPA packages installed")
            logger.warning("  • No project code in current directory")
            logger.info("DSPy Code will still work, but without codebase Q&A features")
        else:
            logger.info(f"✓ Total codebases discovered: {len(codebases)}")

        return codebases

    def should_exclude(self, file_path: Path, base_path: Path) -> bool:
        """Check if a file should be excluded from indexing.

        Args:
            file_path: Path to the file
            base_path: Base path of the codebase

        Returns:
            True if file should be excluded
        """
        relative_path = str(file_path.relative_to(base_path))

        for pattern in self.exclude_patterns:
            # Handle directory patterns
            if pattern.endswith("/"):
                if pattern.rstrip("/") in relative_path.split("/"):
                    return True
            # Handle wildcard patterns
            elif "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(
                    file_path.name, pattern
                ):
                    return True
            # Handle exact matches
            elif pattern in relative_path:
                return True

        return False

    def extract_code_elements(
        self, file_path: Path, codebase_name: str, base_path: Path
    ) -> list[CodeElement]:
        """Extract code elements from a Python file using AST.

        Args:
            file_path: Path to the Python file
            codebase_name: Name of the codebase
            base_path: Base path of the codebase

        Returns:
            List of extracted code elements
        """
        elements = []

        try:
            # Read source code
            source_code = file_path.read_text(encoding="utf-8")

            # Parse with AST
            tree = ast.parse(source_code, filename=str(file_path))

            # Extract imports
            imports = self._extract_imports(tree)

            # Get relative path for cleaner display
            try:
                relative_path = str(file_path.relative_to(base_path))
            except ValueError:
                relative_path = str(file_path)

            # Extract top-level functions and classes
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    element = self._extract_function(
                        node, source_code, relative_path, codebase_name, imports
                    )
                    if element:
                        elements.append(element)

                elif isinstance(node, ast.ClassDef):
                    # Extract the class itself
                    class_element = self._extract_class(
                        node, source_code, relative_path, codebase_name, imports
                    )
                    if class_element:
                        elements.append(class_element)

                    # Extract methods from the class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_element = self._extract_method(
                                item, node.name, source_code, relative_path, codebase_name, imports
                            )
                            if method_element:
                                elements.append(method_element)

        except SyntaxError as e:
            logger.warning(f"Syntax error parsing {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error extracting elements from {file_path}: {e}")

        return elements

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        return imports

    def _extract_decorators(self, node: ast.FunctionDef) -> list[str]:
        """Extract decorator names from a function/method node."""
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorators.append(decorator.func.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(ast.unparse(decorator))
        return decorators

    def _get_docstring(self, node: ast.AST) -> str | None:
        """Extract docstring from a node."""
        return ast.get_docstring(node)

    def _get_source_segment(self, source_code: str, node: ast.AST) -> str:
        """Get the source code for a specific AST node."""
        try:
            return ast.get_source_segment(source_code, node) or ast.unparse(node)
        except:
            return ast.unparse(node)

    def _extract_function(
        self,
        node: ast.FunctionDef,
        source_code: str,
        file_path: str,
        codebase: str,
        imports: list[str],
    ) -> CodeElement | None:
        """Extract a function definition."""
        try:
            return CodeElement(
                type="function",
                name=node.name,
                signature=f"def {node.name}({ast.unparse(node.args)})",
                docstring=self._get_docstring(node),
                code=self._get_source_segment(source_code, node),
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                codebase=codebase,
                imports=imports[:5],  # Keep first 5 imports
                decorators=self._extract_decorators(node),
            )
        except Exception as e:
            logger.debug(f"Error extracting function {node.name}: {e}")
            return None

    def _extract_class(
        self,
        node: ast.ClassDef,
        source_code: str,
        file_path: str,
        codebase: str,
        imports: list[str],
    ) -> CodeElement | None:
        """Extract a class definition."""
        try:
            # Get base classes
            bases = [ast.unparse(base) for base in node.bases]
            bases_str = f"({', '.join(bases)})" if bases else ""

            return CodeElement(
                type="class",
                name=node.name,
                signature=f"class {node.name}{bases_str}",
                docstring=self._get_docstring(node),
                code=self._get_source_segment(source_code, node),
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                codebase=codebase,
                imports=imports[:5],
                decorators=self._extract_decorators(node),
            )
        except Exception as e:
            logger.debug(f"Error extracting class {node.name}: {e}")
            return None

    def _extract_method(
        self,
        node: ast.FunctionDef,
        class_name: str,
        source_code: str,
        file_path: str,
        codebase: str,
        imports: list[str],
    ) -> CodeElement | None:
        """Extract a method definition."""
        try:
            return CodeElement(
                type="method",
                name=f"{class_name}.{node.name}",
                signature=f"def {node.name}({ast.unparse(node.args)})",
                docstring=self._get_docstring(node),
                code=self._get_source_segment(source_code, node),
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                codebase=codebase,
                imports=imports[:5],
                decorators=self._extract_decorators(node),
            )
        except Exception as e:
            logger.debug(f"Error extracting method {class_name}.{node.name}: {e}")
            return None

    def index_codebase(self, name: str, path: Path) -> tuple[CodebaseInfo, list[CodeElement]]:
        """Index a single codebase.

        Args:
            name: Name of the codebase
            path: Path to the codebase root

        Returns:
            Tuple of (CodebaseInfo, list of CodeElements)
        """
        logger.info(f"Indexing codebase: {name} at {path}")

        elements = []
        file_count = 0

        # Find all Python files
        for py_file in path.rglob("*.py"):
            # Skip excluded files
            if self.should_exclude(py_file, path):
                logger.debug(f"Excluding {py_file}")
                continue

            # Extract elements from file
            file_elements = self.extract_code_elements(py_file, name, path)
            elements.extend(file_elements)
            file_count += 1

        # Get version if available
        version = self._get_package_version(name)

        # Create codebase info
        info = CodebaseInfo(
            name=name,
            path=str(path),
            version=version,
            file_count=file_count,
            element_count=len(elements),
            last_indexed=datetime.now(),
        )

        logger.info(f"Indexed {name}: {file_count} files, {len(elements)} elements")

        return info, elements

    def _get_package_version(self, package_name: str) -> str | None:
        """Get the version of an installed package."""
        try:
            # Remove mcp_ prefix if present
            if package_name.startswith("mcp_"):
                return None

            module = importlib.import_module(package_name)
            return getattr(module, "__version__", None)
        except:
            return None

    def build_index(self, force: bool = False) -> CodeIndex:
        """Build complete index of all discovered codebases.

        Args:
            force: Force rebuild even if cache exists

        Returns:
            Complete CodeIndex
        """
        # Try to load from cache first
        if not force:
            cached_index = self.load_index()
            if cached_index and not self.is_index_stale(cached_index):
                logger.info("Using cached index")
                return cached_index

        logger.info("Building new index...")

        # Discover codebases
        codebases = self.discover_codebases()

        if not codebases:
            logger.warning("No codebases discovered")
            return CodeIndex(
                version=self.INDEX_VERSION,
                created_at=datetime.now(),
                codebases={},
                elements=[],
                metadata={},
            )

        # Index each codebase
        all_codebases_info = {}
        all_elements = []

        for name, path in codebases.items():
            try:
                info, elements = self.index_codebase(name, path)
                all_codebases_info[name] = info
                all_elements.extend(elements)
            except Exception as e:
                logger.error(f"Failed to index {name}: {e}")

        # Create index
        index = CodeIndex(
            version=self.INDEX_VERSION,
            created_at=datetime.now(),
            codebases=all_codebases_info,
            elements=all_elements,
            metadata={
                "total_files": sum(info.file_count for info in all_codebases_info.values()),
                "total_elements": len(all_elements),
            },
        )

        # Save to cache
        self.save_index(index)

        logger.info(
            f"Index built: {len(all_codebases_info)} codebases, {len(all_elements)} elements"
        )

        return index

    def save_index(self, index: CodeIndex) -> None:
        """Save index to cache.

        Args:
            index: CodeIndex to save
        """
        try:
            cache_file = self.cache_dir / "index.json.gz"

            # Convert to dict and save as compressed JSON
            index_dict = index.to_dict()
            json_str = json.dumps(index_dict, indent=2)

            with gzip.open(cache_file, "wt", encoding="utf-8") as f:
                f.write(json_str)

            logger.info(f"Index saved to {cache_file}")

        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def load_index(self) -> CodeIndex | None:
        """Load index from cache.

        Returns:
            CodeIndex if cache exists, None otherwise
        """
        try:
            cache_file = self.cache_dir / "index.json.gz"

            if not cache_file.exists():
                logger.debug("No cached index found")
                return None

            # Load compressed JSON
            with gzip.open(cache_file, "rt", encoding="utf-8") as f:
                json_str = f.read()

            index_dict = json.loads(json_str)
            index = CodeIndex.from_dict(index_dict)

            logger.info(f"Index loaded from cache: {len(index.elements)} elements")
            return index

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return None

    def is_index_stale(self, index: CodeIndex, max_age_days: int = 7) -> bool:
        """Check if index needs refresh.

        Args:
            index: CodeIndex to check
            max_age_days: Maximum age in days before considering stale

        Returns:
            True if index is stale
        """
        age = datetime.now() - index.created_at
        return age > timedelta(days=max_age_days)

    def get_cache_size(self) -> int:
        """Get total size of cache directory in bytes."""
        total_size = 0
        for file in self.cache_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size

    def clear_cache(self) -> None:
        """Clear all cached index files."""
        try:
            for file in self.cache_dir.rglob("*"):
                if file.is_file():
                    file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
