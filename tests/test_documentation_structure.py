#!/usr/bin/env python3
"""
Tests for documentation structure and consistency.

This test module validates that the README files maintain proper structure
and that the API documentation is consistent between English and Chinese versions.
"""

import unittest
import re
import os
from pathlib import Path


class TestDocumentationStructure(unittest.TestCase):
    """Test documentation structure and consistency."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.readme_en = self.project_root / "README.md"
        self.readme_zh = self.project_root / "README.zh-CN.md"
        self.copilot_instructions = self.project_root / ".github" / "copilot-instructions.md"
    
    def test_readme_files_exist(self):
        """Test that both README files exist."""
        self.assertTrue(self.readme_en.exists(), "English README.md not found")
        self.assertTrue(self.readme_zh.exists(), "Chinese README.zh-CN.md not found")
        self.assertTrue(self.copilot_instructions.exists(), "Copilot instructions not found")
    
    def test_api_reference_structure_english(self):
        """Test that English README has proper API Reference structure."""
        with open(self.readme_en, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for main API Reference section
        self.assertIn("## 📚 API Reference", content, "API Reference section not found")
        
        # Check for required subsections
        expected_sections = [
            "### 💬 Chat Operations",
            "### 🛠️ Chat Management", 
            "### 🤖 Model Management",
            "### 📚 Knowledge Base Operations",
            "### 📝 Notes API",
            "### 📊 Return Value Examples"
        ]
        
        for section in expected_sections:
            self.assertIn(section, content, f"Missing section: {section}")
    
    def test_api_reference_structure_chinese(self):
        """Test that Chinese README has proper API Reference structure."""
        with open(self.readme_zh, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for main API Reference section
        self.assertIn("## 📚 API 参考", content, "API Reference section not found")
        
        # Check for required subsections
        expected_sections = [
            "### 💬 聊天操作",
            "### 🛠️ 聊天管理",
            "### 🤖 模型管理", 
            "### 📚 知识库操作",
            "### 📝 笔记 API",
            "### 📊 返回值示例"
        ]
        
        for section in expected_sections:
            self.assertIn(section, content, f"Missing section: {section}")
    
    def test_no_duplicate_chat_methods(self):
        """Test that there are no duplicate chat() method entries."""
        with open(self.readme_en, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all chat() method entries in tables
        chat_method_pattern = r'\| `chat\(\)` \|'
        matches = re.findall(chat_method_pattern, content)
        
        # Should only have one chat() method entry in the API Reference
        self.assertEqual(len(matches), 1, f"Found {len(matches)} chat() entries, expected 1")
    
    def test_table_structure_consistency(self):
        """Test that API tables have consistent structure."""
        for file_path, language in [(self.readme_en, 'English'), (self.readme_zh, 'Chinese')]:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all table headers in API Reference section - use more robust pattern
            api_section_pattern = r'## 📚 API Reference.*?(?=^## |\Z)' if language == 'English' else r'## 📚 API 参考.*?(?=^## |\Z)'
            api_section_match = re.search(api_section_pattern, content, re.MULTILINE | re.DOTALL)
            if api_section_match:
                api_section = api_section_match.group()
                
                # Check that tables have the expected 3-column structure
                header_pattern = '| Method | Description | Parameters |' if language == 'English' else '| 方法 | 说明 | 参数 |'
                table_headers_count = api_section.count(header_pattern)
                
                # Should have multiple properly structured tables
                self.assertGreater(table_headers_count, 0, f"{language}: No properly structured tables found")
            else:
                self.fail(f"{language}: API Reference section not found")
    
    def test_copilot_instructions_enhanced(self):
        """Test that copilot instructions have been enhanced with API documentation guidelines."""
        with open(self.copilot_instructions, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for new API documentation sections
        expected_sections = [
            "## API文档维护规范",
            "### 1. API Reference 组织原则",
            "### 2. 文档同步维护流程",
            "### 3. API文档质量标准",
            "## 故障排除文档规范"
        ]
        
        for section in expected_sections:
            self.assertIn(section, content, f"Missing copilot instruction section: {section}")
    
    def test_return_value_examples_present(self):
        """Test that return value examples are present in both README files."""
        for file_path, language in [(self.readme_en, 'English'), (self.readme_zh, 'Chinese')]:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for code blocks with return value examples
            code_block_pattern = r'```python.*?```'
            code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
            
            # Should have at least some code examples in the API Reference section
            self.assertGreater(len(code_blocks), 0, f"{language}: No code examples found")
            
            # Check for specific return value patterns
            expected_patterns = [
                '"response":', '"chat_id":', '"message_id":'
            ]
            
            found_patterns = 0
            for pattern in expected_patterns:
                if pattern in content:
                    found_patterns += 1
            
            self.assertGreater(found_patterns, 0, f"{language}: No return value examples found")


if __name__ == '__main__':
    unittest.main()