import os
import platform
from typing import Optional, Type

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


# 创建一个桌面文件夹
def create_folder_on_desktop(folder_name: Optional[str] = None) -> str:
    if not folder_name:
        folder_name = 'workspace'

    # 获取当前操作系统
    os_type = platform.system()
    # print(os_type)

    # 根据操作系统获取桌面路径
    if os_type == "Windows":
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif os_type == "Darwin":  # macOS 的系统名称是 "Darwin"
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        raise OSError("Unsupported operating system")

    # 创建文件夹路径
    folder_path = os.path.join(desktop_path, folder_name)

    # 如果文件夹不存在，则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


class WriteDocument(BaseModel):
    filename: str = Field(description="The name of the file")
    file_content: str = Field(description="Contents of the file")


class WriteFilesTool(BaseTool):
    name = "write_document"
    description = "Write the file contents to the file."
    args_schema: Type[BaseModel] = WriteDocument
    return_direct: bool = False

    def _run(
        self, filename: str, file_content: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Write the file contents to the file."""

        # 文件夹的名称
        folder_name = 'workspace'
        # 获取桌面文件夹路径
        current_path = create_folder_on_desktop(folder_name)
        # 创建并写入内容到 .md 文件
        file_path = os.path.join(current_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return "The file has been written successfully."

    async def _arun(
        self,
        a: int,
        b: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


if __name__ == '__main__':
    # folder_name = 'workspace'
    # print(create_folder_on_desktop(folder_name))

    write_doc = WriteFilesTool()
    print(write_doc.name)
    print(write_doc.description)
    print(write_doc.args)
    # 测试下来invoke中的参数需要严格和tool方法中的参数保持一致
    # write_doc.invoke({'filename': 'readme.md', 'file_content': '## readme'})
