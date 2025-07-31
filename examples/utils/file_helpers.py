#!/usr/bin/env python3
"""
File helper utilities for OpenWebUI Chat Client examples.

This module provides utilities for creating, managing, and cleaning up test files
used in examples, including text files, images, and other resources.

Features provided:
- Test file creation and cleanup
- Image generation for multimodal examples
- Temporary file management
- Batch file operations

Usage:
    from utils.file_helpers import FileHelper, TestFileManager
    
    # Create a test file
    file_path = FileHelper.create_text_file("test.txt", "content")
    
    # Manage multiple files
    manager = TestFileManager()
    file1 = manager.create_test_file("file1.txt", "content1")
    file2 = manager.create_test_file("file2.txt", "content2")
    manager.cleanup_all()  # Clean up all created files
"""

import logging
import os
import tempfile
from typing import List, Optional, Dict, Any
from pathlib import Path

# Optional PIL import for image creation
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileHelper:
    """Static helper methods for file operations."""
    
    @staticmethod
    def create_text_file(filename: str, content: str, encoding: str = "utf-8") -> Optional[str]:
        """
        Create a text file with the specified content.
        
        Args:
            filename: Name of the file to create
            content: Text content to write to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            File path if successful, None if failed
        """
        try:
            with open(filename, "w", encoding=encoding) as f:
                f.write(content)
            logger.info(f"✅ Created text file: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to create text file {filename}: {e}")
            return None

    @staticmethod
    def create_test_image(text: str, filename: str, size: tuple = (500, 100), 
                         bg_color: tuple = (20, 40, 80), text_color: tuple = (255, 255, 200)) -> Optional[str]:
        """
        Create a test image with text overlay.
        
        Args:
            text: Text to display on the image
            filename: Name of the image file to create
            size: Image size as (width, height) tuple
            bg_color: Background color as RGB tuple
            text_color: Text color as RGB tuple
            
        Returns:
            File path if successful, None if failed
        """
        if not PIL_AVAILABLE:
            logger.warning("❌ PIL (Pillow) not available. Cannot create test image.")
            return None
            
        try:
            img = Image.new("RGB", size, color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fall back to default
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except (IOError, OSError):
                try:
                    # Try a few common font paths
                    font_paths = [
                        "/System/Library/Fonts/Arial.ttf",  # macOS
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                        "C:/Windows/Fonts/arial.ttf"  # Windows
                    ]
                    font = None
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, 30)
                            break
                    if not font:
                        font = ImageFont.load_default()
                except Exception:
                    font = ImageFont.load_default()
            
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill=text_color, font=font)
            img.save(filename)
            logger.info(f"✅ Created test image: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to create test image {filename}: {e}")
            return None

    @staticmethod
    def create_json_file(filename: str, data: Dict[Any, Any]) -> Optional[str]:
        """
        Create a JSON file with the specified data.
        
        Args:
            filename: Name of the JSON file to create
            data: Dictionary data to serialize to JSON
            
        Returns:
            File path if successful, None if failed
        """
        try:
            import json
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Created JSON file: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to create JSON file {filename}: {e}")
            return None

    @staticmethod
    def cleanup_files(filenames: List[str]) -> None:
        """
        Remove multiple files.
        
        Args:
            filenames: List of file paths to remove
        """
        for filename in filenames:
            if filename and os.path.exists(filename):
                try:
                    os.remove(filename)
                    logger.info(f"🧹 Cleaned up file: {filename}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clean up file {filename}: {e}")

    @staticmethod
    def read_file(filename: str, encoding: str = "utf-8") -> Optional[str]:
        """
        Read content from a text file.
        
        Args:
            filename: Path to the file to read
            encoding: File encoding (default: utf-8)
            
        Returns:
            File content if successful, None if failed
        """
        try:
            with open(filename, "r", encoding=encoding) as f:
                content = f.read()
            logger.debug(f"📖 Read file: {filename}")
            return content
        except Exception as e:
            logger.error(f"❌ Failed to read file {filename}: {e}")
            return None

    @staticmethod
    def file_exists(filename: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(filename) and os.path.isfile(filename)


class TestFileManager:
    """
    Manager for creating and cleaning up test files.
    
    This class keeps track of all files created and provides
    easy cleanup functionality.
    """
    
    def __init__(self, auto_cleanup: bool = True):
        """
        Initialize the test file manager.
        
        Args:
            auto_cleanup: Whether to automatically cleanup files on destruction
        """
        self.created_files: List[str] = []
        self.auto_cleanup = auto_cleanup
        
    def create_test_file(self, filename: str, content: str, 
                        file_type: str = "text") -> Optional[str]:
        """
        Create a test file and track it for cleanup.
        
        Args:
            filename: Name of the file to create
            content: Content for the file
            file_type: Type of file ('text', 'json', 'image')
            
        Returns:
            File path if successful, None if failed
        """
        if file_type == "text":
            file_path = FileHelper.create_text_file(filename, content)
        elif file_type == "json":
            import json
            data = json.loads(content) if isinstance(content, str) else content
            file_path = FileHelper.create_json_file(filename, data)
        elif file_type == "image":
            file_path = FileHelper.create_test_image(content, filename)
        else:
            logger.error(f"❌ Unsupported file type: {file_type}")
            return None
            
        if file_path:
            self.created_files.append(file_path)
            
        return file_path
    
    def create_temp_file(self, content: str, suffix: str = ".txt", 
                        prefix: str = "test_") -> Optional[str]:
        """
        Create a temporary file with automatic naming.
        
        Args:
            content: Content for the file
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            File path if successful, None if failed
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, prefix=prefix, 
                                           delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name
            
            self.created_files.append(temp_path)
            logger.info(f"✅ Created temporary file: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"❌ Failed to create temporary file: {e}")
            return None
    
    def create_test_files_batch(self, files_data: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Create multiple test files at once.
        
        Args:
            files_data: Dictionary mapping filenames to content
            
        Returns:
            Dictionary mapping filenames to file paths (or None if failed)
        """
        results = {}
        for filename, content in files_data.items():
            results[filename] = self.create_test_file(filename, content)
        return results
    
    def cleanup_all(self) -> None:
        """Clean up all created files."""
        if self.created_files:
            logger.info(f"🧹 Cleaning up {len(self.created_files)} test files...")
            FileHelper.cleanup_files(self.created_files)
            self.created_files.clear()
    
    def get_created_files(self) -> List[str]:
        """Get list of all created files."""
        return self.created_files.copy()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup_all()
    
    def __del__(self):
        """Destructor with optional auto-cleanup."""
        if self.auto_cleanup:
            self.cleanup_all()


# Predefined test content for common use cases
class TestContent:
    """Common test content for examples."""
    
    BLOCKCHAIN_CONTENT = """
    The Ouroboros protocol is a family of proof-of-stake blockchain protocols 
    that provide verifiable security guarantees. It was the first blockchain 
    protocol to be based on peer-reviewed research and to provide 
    mathematically-verified security guarantees.
    """
    
    AI_CONTENT = """
    Artificial Intelligence (AI) refers to the simulation of human intelligence 
    in machines that are programmed to think and learn like humans. The term 
    may also be applied to any machine that exhibits traits associated with 
    a human mind such as learning and problem-solving.
    """
    
    SPACE_CONTENT = """
    Project Apollo was a series of space missions conducted by NASA between 
    1961 and 1972. The primary objective was to land humans on the Moon and 
    bring them back safely to Earth. Apollo 11 was the first mission to 
    achieve this goal in July 1969.
    """
    
    PYTHON_CONTENT = """
    Python is a high-level, interpreted programming language with dynamic 
    semantics. Its high-level built-in data structures, combined with dynamic 
    typing and dynamic binding, make it very attractive for Rapid Application 
    Development, as well as for use as a scripting or glue language.
    """
    
    @classmethod
    def get_sample_data(cls) -> Dict[str, str]:
        """Get all sample content as a dictionary."""
        return {
            "blockchain.txt": cls.BLOCKCHAIN_CONTENT.strip(),
            "ai.txt": cls.AI_CONTENT.strip(),
            "space.txt": cls.SPACE_CONTENT.strip(),
            "python.txt": cls.PYTHON_CONTENT.strip()
        }


if __name__ == "__main__":
    # Example usage
    with TestFileManager() as manager:
        # Create some test files
        file1 = manager.create_test_file("test1.txt", "This is test content 1")
        file2 = manager.create_test_file("test2.txt", "This is test content 2")
        
        if PIL_AVAILABLE:
            image = manager.create_test_file("test.png", "Hello World!", "image")
        
        print(f"Created files: {manager.get_created_files()}")
        # Files will be automatically cleaned up when exiting the context