import os.path

def write_file(working_directory, file_path, content=""):
    fullpath_working_directory = os.path.abspath(working_directory)
    fullpath_file = os.path.abspath(os.path.join(fullpath_working_directory,file_path))
    fullpath_directory = os.path.dirname(fullpath_file)

    if not fullpath_directory.startswith(fullpath_working_directory):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    try:
        if not os.path.exists(fullpath_file):
            os.makedirs(fullpath_directory, exist_ok=True)
        
        with open(fullpath_file, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {e}"