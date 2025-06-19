
import os.path
import subprocess

def run_python_file(working_directory, file_path, arglist=[], timeout=30):
    fullpath_working_directory = os.path.abspath(working_directory)
    fullpath_file = os.path.abspath(os.path.join(fullpath_working_directory,file_path))
    fullpath_directory = os.path.dirname(fullpath_file)

    if not fullpath_directory.startswith(fullpath_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(fullpath_file):
        return f'Error: File "{file_path}" not found.'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        exe_args = ["python", fullpath_file]
        if arglist:
            exe_args.extend(arglist)
        result = subprocess.run(
            exe_args,
            cwd=fullpath_working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout 
        )

        has_output = False

        output = []

        if result.stdout :
            output.append(f"STDOUT: {result.stdout}")
            has_output = True

        if result.stderr :
            output.append(f"STDERR: {result.stderr}")
            has_output = True

        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        if not has_output:
            output.append("No output produced.")
        
        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return "Error: The process was terminated because it exceeded the maximum allowed execution time of 30 seconds."
    except Exception as e:
        return f"Error: executing Python file: {e}"