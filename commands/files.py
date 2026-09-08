import os

class FilesTool:
    def create_folder(self, folder_name: str) -> str:
        if not folder_name:
            return "Folder name cannot be empty."
        try:
            os.makedirs(folder_name, exist_ok=True)
            return f"Successfully created folder '{folder_name}'."
        except Exception as e:
            return f"Failed to create folder: {str(e)}"
            
    def list_files(self, directory: str = ".") -> str:
        try:
            files = os.listdir(directory)
            if not files:
                return "The directory is empty."
            return "Files in current directory:\n" + "\n".join(f"- {f}" for f in files)
        except Exception as e:
            return f"Failed to list directory: {str(e)}"
            
    def check_exists(self, path: str) -> str:
        if os.path.exists(path):
            if os.path.isdir(path):
                return f"The folder '{path}' exists."
            return f"The file '{path}' exists."
        return f"'{path}' does not exist."
