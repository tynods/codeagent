import sys
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_file_content import MAX_CHARS
from functions.call_function import call_function

model_name = "gemini-2.0-flash-001"

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. 
You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files
- Write or overwrite files

All paths you provide should be relative to the working directory (also called root in this context which path is '.').
You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

def main(user_prompt, verbose=False):

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")


    client = genai.Client(api_key=api_key)

    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Returns the content of a file specified with its path relative to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description=f"The file path of the file which content is wanted, relative to the working directory. The returned content is restricted to {MAX_CHARS} characters",
                ),
            },
        ),
    )

    
    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Write the provided content to a file which path os provided, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path of the file to write to, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="Content to write to the file",
                ),
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="""Execute the Python file provided by its filepath. 
            The optional arguments are passed as an array and provided in the command line.
            Returns the stdout and stderr along with errors if any""",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path of the file to execute, relative to the working directory.",
                ),
                "arglist": types.Schema(
                    type=types.Type.ARRAY,
                    description="List of the commande line arguments to be passed to the Python script.",
                    items=types.Schema(
                        type=types.Type.STRING,
                    ),
                ),
            },
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            # schema_run_python_file
        ]
    )

    config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
    )

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    
    if verbose:
        print(f"User prompt: {user_prompt}")

    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config
    )

    # print(response.candidates)
    last_text = ""
    nb_iter = 20
    while nb_iter>0:
        # print("iter", nb_iter)
        nb_iter -= 1
        for candidate in response.candidates:
            # print("*CANDIDATE*", candidate)
            messages.append(candidate.content)
            for part in candidate.content.parts:
                # print("*PART*", part)
                did_function_call = False
                if part.function_call:
                    # print("**part.function_call**", part.function_call)
                    for function_call_part in response.function_calls:
                        function_call_result = call_function(function_call_part, verbose)
                        did_function_call = True
                        if verbose:
                            try:
                                print(print(f"-> {function_call_result.parts[0].function_response.response}"))
                            except Exception as e:
                                raise RuntimeError("function call error : {e}")
                        messages.append(function_call_result)
                if part.text:
                    # print(part.text)
                    last_text = part.text
            if not did_function_call :
                # print("- DONE -")
                print(last_text)
                nb_iter = 0
                break
        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=config
        )
        



    # if response.function_calls:
    #     for function_call_part in response.function_calls:
    #         # print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    #         function_call_result = call_function(function_call_part, verbose)
    #         if verbose:
    #             try:
    #                 print(print(f"-> {function_call_result.parts[0].function_response.response}"))
    #             except Exception as e:
    #                 raise RuntimeError("function call error : {e}")

    # else :
    #     print(response.text)

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__=="__main__":
    if len(sys.argv)<2:
        print("Missing prompt !")
        sys.exit(1)
    else :
        is_verbose = False
        if len(sys.argv)>2:
            is_verbose = True if sys.argv[2]=="--verbose" else False
        main(sys.argv[1], is_verbose)