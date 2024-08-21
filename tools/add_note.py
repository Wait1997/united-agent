"""添加备忘录"""
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from utils.utils import get_os_type
import os


class NoteParams(BaseModel):
    title: str = Field(description="Title of the note (Title of the memo).")
    content: str = Field(description="Contents of the note (Contents of the memorandum).")


@tool("add-note", args_schema=NoteParams)
def add_note(title: str, content: str):
    """Open the system notes (Open System Memo), write the corresponding title and content."""

    os_type = get_os_type()

    if os_type == 'macOS':
        """在macOS上打开备忘录应用并写入内容"""
        # macOS可以通过AppleScript打开备忘录并插入内容
        apple_script = f'''
            tell application "Notes"
                activate
                tell account "iCloud"
                    set newNote to make new note at folder "Notes" with properties {{name:"{title}", body:"{content}"}}
                end tell
            end tell
            '''
        os.system(f"osascript -e '{apple_script}'")
        return '备忘录打开了并且写入完成了'

    elif os_type == 'Windows':
        return '便笺还不能打开'

    else:
        return 'Unsupported platform'


if __name__ == '__main__':
    print(add_note.name)
    print(add_note.invoke({'title': 'beauty girl', 'content': 'a very beautiful girl lucy.'}))
