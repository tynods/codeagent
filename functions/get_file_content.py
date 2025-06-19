import os.path

MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    fullpath_working_directory = os.path.abspath(working_directory)
    fullpath_file = os.path.abspath(os.path.join(fullpath_working_directory,file_path))
    fullpath_directory = os.path.dirname(fullpath_file)

    if not fullpath_directory.startswith(fullpath_working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(fullpath_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:

        with open(fullpath_file, "r") as f:
            file_content_string = f.read(MAX_CHARS)

        if os.path.getsize(fullpath_file)>MAX_CHARS:
            file_content_string += "\n"+f'[...File "{file_path}" truncated at 10000 characters]'

        return file_content_string

    except Exception as e:
        return f"Error: {e}"