import re
from typing import Dict, Union, Optional
from utils import get_os_type


class BasicMatcher:
    """匹配系统应用名称"""
    def __init__(self, default_patterns=None):
        if default_patterns is None:
            default_patterns = {}

        # 获取当前操作系统类型
        self.os_type = get_os_type()
        if self.os_type == 'Windows':
            self.default_patterns = {
                "Notes": r'(?i)\b(Note|Notes|Memo|备忘录|笔记|便笺)\b',
                "code": r'(?i)(Visual Studio Code|VisualStudioCode|vscode|vs code|code)',
                **default_patterns
            }
        elif self.os_type == 'macOS':
            self.default_patterns = {
                "Notes": r'(?i)\b(Note|Notes|Memo|备忘录|笔记|便笺)\b',
                "Visual Studio Code": r'(?i)(Visual Studio Code|VisualStudioCode|vscode|vs code|code)',
                **default_patterns
            }
        else:
            raise EnvironmentError('Unsupported platform.')
        self.app_patterns = self.default_patterns.copy()  # 初始化时使用默认规则

    def add_rule(self, app_name: str, pattern: str):
        """添加或更新应用匹配规则，如果应用名称已存在则抛出异常"""
        if app_name in self.app_patterns:
            raise ValueError(f"应用名称 '{app_name}' 已经存在")
        self.app_patterns[app_name] = pattern

    def match_app(self, input_content: str) -> Union[str, None]:
        """匹配输入字符串并返回应用名称"""
        for app_name, pattern in self.app_patterns.items():
            if re.search(pattern, input_content):
                return app_name
        return None

    def reset_to_default(self) -> None:
        """重置为默认匹配规则"""
        self.app_patterns = self.default_patterns.copy()
