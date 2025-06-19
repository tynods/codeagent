from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

WORKING_DIR = "./calculator"

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = function_call_part.args

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else :
        print(f" - Calling function: {function_name}")

    dic_func = {
        "get_files_info" : (get_files_info, [("directory",False)]),
        "get_file_content" : (get_file_content, [("file_path",True)]),
        "write_file" : (write_file, [("file_path",True), ("content",False)]),
        "run_python_file" : (run_python_file, [("file_path",True),("arglist",False)])
    }
    
    if function_name not in dic_func:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    function, list_args_req = dic_func[function_name]

    missing_params = list(filter(lambda x: x[1] and x[0] not in args, list_args_req))

    if len(missing_params)>0:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"parameter '{missing_params[0]}' is missing in the call of function: {function_name}"},
                )
            ],
        )
    
    function_result = function(WORKING_DIR, *[args[x[0]] for x in list_args_req if x[0] in args]) # on a déjà vérifier si required ou pas

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )