#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست‌های اولیه برای AI-Agent-Manager
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from agent_builder import AgentBuilder


class TestAgentBuilder(unittest.TestCase):
    """تست‌های کلاس AgentBuilder"""

    def setUp(self):
        """تنظیمات اولیه قبل از هر تست"""
        self.test_dir = tempfile.mkdtemp()
        self.builder = AgentBuilder(
            workspace_dir=self.test_dir,
            config_path='test_config.json'
        )

    def tearDown(self):
        """پاکسازی بعد از هر تست"""
        shutil.rmtree(self.test_dir)

    def test_config_loading(self):
        """تست بارگذاری تنظیمات"""
        self.assertIn('supported_agent_types', self.builder.config)
        self.assertIn('developer', self.builder.config['supported_agent_types'])

    def test_tool_detection(self):
        """تست تشخیص ابزار"""
        # ابزار باید تشخیص داده شود (یا opencode یا freebuff)
        self.assertIn(self.builder.selected_tool, ['opencode', 'freebuff'])

    def test_agent_id_generation(self):
        """تست تولید شناسه ایجنت"""
        agent_id = self.builder._generate_agent_id('developer', 'تست')
        self.assertTrue(agent_id.startswith('agent_developer_'))
        self.assertIn('_', agent_id)

    def test_prompt_creation(self):
        """تست ایجاد پرامپت"""
        prompt = self.builder._create_agent_prompt(
            'developer',
            'ایجنت توسعه',
            'python'
        )
        self.assertIn('developer', prompt)
        self.assertIn('ایجنت توسعه', prompt)

    def test_list_agents_empty(self):
        """تست لیست ایجنت‌ها (خالی)"""
        agents = self.builder.list_agents()
        self.assertEqual(len(agents), 0)

    def test_agent_types_validation(self):
        """تست اعتبارسنجی نوع ایجنت"""
        # نوع معتبر
        self.assertIn('developer', self.builder.config['supported_agent_types'])
        
        # نوع نامعتبر
        self.assertNotIn('invalid_type', self.builder.config['supported_agent_types'])


class TestAgentBuilderIntegration(unittest.TestCase):
    """تست‌های یکپارچه"""

    def setUp(self):
        """تنظیمات اولیه"""
        self.test_dir = tempfile.mkdtemp()
        # ایجاد تنظیمات تست
        config = {
            'tools_priority': ['opencode', 'freebuff'],
            'supported_agent_types': ['developer', 'research']
        }
        config_path = Path(self.test_dir) / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        self.builder = AgentBuilder(
            workspace_dir=self.test_dir,
            config_path='config.json'
        )

    def tearDown(self):
        """پاکسازی"""
        shutil.rmtree(self.test_dir)

    def test_prompt_building(self):
        """تست ساخت پرامپت"""
        prompt = self.builder._build_prompt(
            'تست',
            {'agent_type': 'developer', 'language': 'python'},
            'freebuff'
        )
        self.assertIn('تست', prompt)
        self.assertIn('developer', prompt)


if __name__ == '__main__':
    unittest.main()
