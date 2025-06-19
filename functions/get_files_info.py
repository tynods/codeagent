
import os.path

def get_files_info(working_directory, directory=""):
    fullpath_working_directory = os.path.abspath(working_directory)
    fullpath_directory = os.path.abspath(os.path.join(working_directory, directory))

    if not fullpath_directory.startswith(fullpath_working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    if not os.path.isdir(fullpath_directory):
        return f'Error: "{directory}" is not a directory'
    
    
    
    info = []
    for elt in os.listdir(fullpath_directory):
        try :
            fullpath = os.path.join(fullpath_directory, elt)
            is_dir = os.path.isdir(fullpath)
            # is_file = os.path.isfile(fullpath)
            size = os.path.getsize(fullpath)

            info.append(f"- {elt}: file_size={size} bytes, is_dir={is_dir}")
        except Exception as e:
            return f"Error: {e}"
    return "\n".join(info)