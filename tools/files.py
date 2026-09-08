import os
from .base import BaseTool

class CreateFolderTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_folder"

    @property
    def description(self) -> str:
        return "Creates a new folder on the file system."

    @property
    def parameters_schema(self) -> dict:
        return {"folder_name": "string"}

    def execute(self, folder_name: str = "", **kwargs) -> str:
        if not folder_name:
            return "Folder name cannot be empty."
        try:
            os.makedirs(folder_name, exist_ok=True)
            return f"Successfully created folder '{folder_name}'."
        except Exception as e:
            return f"Failed to create folder: {str(e)}"

class ListFilesTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "Lists all files and folders in the current directory."

    @property
    def parameters_schema(self) -> dict:
        return {}

    def execute(self, **kwargs) -> str:
        try:
            files = os.listdir(".")
            if not files:
                return "The directory is empty."
            return "Files in current directory:\n" + "\n".join(f"- {f}" for f in files)
        except Exception as e:
            return f"Failed to list directory: {str(e)}"

class CheckExistsTool(BaseTool):
    @property
    def name(self) -> str:
        return "check_exists"

    @property
    def description(self) -> str:
        return "Checks if a specific file or folder path exists."

    @property
    def parameters_schema(self) -> dict:
        return {"path": "string"}

    def execute(self, path: str = "", **kwargs) -> str:
        if not path:
            return "Please specify a path."
        if os.path.exists(path):
            if os.path.isdir(path):
                return f"The folder '{path}' exists."
            return f"The file '{path}' exists."
        return f"'{path}' does not exist."
