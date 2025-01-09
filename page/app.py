from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI
import seaborn as sns
import pandas as pd
import numpy as np
import json
import time
import os
import re

load_dotenv()
BASE_UPLOAD_PATH = "page/uploads"
UPLOAD_FOLDER = os.path.join(os.getcwd(), BASE_UPLOAD_PATH)
SUMMARY_FILE = os.path.join(os.getcwd(), BASE_UPLOAD_PATH, "summary.json")
ALLOWED_PREFIXES = {"pd.", "np.", "plt.", "sns."}
ALLOWED_BUILT_INS = {
    "abs", "all", "any", "divmod", "max", "min", "pow", "round", "sum",
    "len", "sorted", "reversed", "range",
    "float", "int", "str", "list", "tuple", "dict", "set", "complex", "bytes",
    "bool", "enumerate", "zip", "map", "filter", "next",
    "type", "isinstance", "id", "hash"
}

# Initialize the Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# Custom filter for basename
@app.template_filter('basename')
def basename_filter(value):
    return os.path.basename(value)

# Set the upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route for the homepage
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    uploaded_files = request.files.getlist("file")
    message = request.form.get("message")

    # Save files and create a list of file paths
    file_paths = []
    for file in uploaded_files:
        if file.filename:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
            file.save(file_path)
            file_paths.append(file_path)

    # Pass file paths to the chat template
    return render_template("chat.html", file_paths=file_paths, message=message)

@socketio.on("process")
def process(data):
    file_paths = data.get("file_paths")
    message = data.get("message")
    conversation_history = data.get("conversation_history")
    num_images = data.get("num_images")
    summaries = {}

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        
        # Create file summary (supports CSV, JSON, and Excel files)
        try:
            if file_name.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_name.endswith('.json'):
                data = pd.read_json(file_path)
            elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                data = pd.read_excel(file_path)
            else:
                socketio.emit("update_chatbox", {"message": f"Unsupported file format: {file_name}. Please upload a valid file."})
                return
        except Exception as e:
            socketio.emit("update_chatbox", {"message": f"Error reading file: {file_name}. Please upload a valid file."})
            return

        column_info = ""
        for col in data.columns:
            column_info += f"[{col},{data[col].nunique()},{data[col].dtype}],"

        summary_text = f"Data file name: {file_name}\nNumber of rows: {data.shape[0]}\nColumn info with format [name,num unique values,type]:[{column_info[0:-1]}]"
        summaries[file_name] = summary_text

        # Send update for the current file
        socketio.emit("update_chatbox", {"message": f'Processed: <strong>{file_name}</strong>'})

        # Wait for 1 second before processing the next file
        time.sleep(1)
    
    # Save all summaries to the summary.json file
    summaries.update(summaries)

    with open(SUMMARY_FILE, "w") as f:
        json.dump(summaries, f, indent=4)

    # Send a file processing completion message
    socketio.emit("update_chatbox", {"message": "All files processed successfully!"})
    
    # Prompts
    system_prompt = """
        ALWAYS follow the following instructions. Do not deviate:
        1. You will receive information about user-uploaded data and a question posed by the user. Determine which function(s) to call to answer this question, using the available information.
        2. You ONLY have access to: built-in Python, numpy, pandas, matplotlib, and seaborn functions. When using one of the libraries, make sure to use np., pd., plt. or sns. as a suffix for the function.
        3. If you think you can answer the question, return the following format. You can read this as RESULT# = function_name(param1=value1,param2=value2).
        {
            "Next": "START",
            "RESULT1": {
                "function": "function_name",
                "parameters": {
                    "param1": "value1",
                    "param2": "value2",
                    ...
                }
            },
            "RESULT2": {
                "function": "function_name",
                "parameters": {
                    "param1": "RESULT1",
                    "param2": "value2",
                    ...
                }
            },
            ...
        }
        4. If you can answer the question with the current information, return:
        {
            'Next': 'FORMAT',
            'Formatted': 'formatted_answer'
        }
        5. DO NOT add comments, ```python code blocks```, or any other formatting or code to the response. ONLY return one of the three fitting JSON formats above.
        6. You can use pd.read_... for reading data.
        7. If you need to plot, use the plt.show() function. The plot will be saved and displayed to the user.
    """

    init_prompt = f"""
    {summaries}
    ---
    User Question: {message}
    """

    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("API_KEY"))
    model = os.getenv("MODEL")
    
    if len(conversation_history) == 0:
        # o1-preview and o1-mini don't support system role
        if model != "o1-preview" and model != "o1-mini":
            conversation_history.append({"role": "system", "content": system_prompt})
        else:
            conversation_history.append({"role": "user", "content": system_prompt})
    
    # Initial user prompt
    user_prompt = {"role": "user", "content": init_prompt}
    conversation_history.append(user_prompt)
    
    # Send waiting message to chatbox
    socketio.emit("update_chatbox", {"message": "Figuring out which functions to run..."})
    
    answer_type = ''
    attempts = 0
    while True:
        attempts += 1
        print("\n", attempts, conversation_history, "\n")
        
        # Dev check
        # stopIt = input(f"Current attempt: {attempts}. Want to stop? Enter Y, anything else will continue.")
        # if stopIt == "Y": break
        if attempts > 3 and answer_type != "FORMAT":
            socketio.emit("update_chatbox", {"message": "Oops! Model failed to generate a valid answer, please try again."})
        
        # Call model
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
        )
        
        # Extract assistant's response
        assistant_response = chat_completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_response})
        print("\n", assistant_response, "\n")
        
        # Process and validate response
        socketio.emit("update_chatbox", {"message": "Validating functions..." })
        processed = preprocess_json(assistant_response)
        answer_type, valid = validate_ai_response(processed)
        
        # If the response was invalid
        if not valid:
            invalid_prompt = f"An error occurred when running the given functions: {answer_type}. Please rethink your response and try again."
            print(invalid_prompt)
            conversation_history.append({"role": "user", "content": invalid_prompt})
            continue
        
        # Put everything else in a try/except block and return any errors to model
        try: 
            processed = json.loads(processed)
            
            if answer_type == 'FORMAT': # If it's a formatted answer, just send it to box
                socketio.emit("update_chatbox", {"message": f"{processed.get('Formatted')}" })
                break
            elif answer_type == 'START': # If it's a function list, try running functions and send image to box OR format-request to AI
                socketio.emit("update_chatbox", {"message": "Running functions..." })
                results, isPlot = execute_agent_instructions(processed, os.path.join("page/static/images", f"plot_{num_images}.png"))
                if isPlot:
                    socketio.emit("update_chatbox", {"message": f"{results}" })
                    num_images += 1
                    break
                else:
                    format_prompt = f"Following is a dictionary with the results of all given functions in order, please use this to give a FORMAT response in the earlier JSON format: {results}"
                    print(format_prompt)
                    conversation_history.append({"role": "user", "content": format_prompt})
                    continue
            elif answer_type == "ERROR": # If there's an error, send it to box
                socketio.emit("update_chatbox", {"message": f"{processed.get('Reason')}" })
                break
        except Exception as exc:
            error_prompt = f"An error occurred when running the given functions: {exc}. Please rethink your response and try again."
            conversation_history.append({"role": "user", "content": error_prompt})
            continue
    # Emit event to notify the client that processing is done
    socketio.emit("process_finished", { "conversation_history" : conversation_history, "num_images": num_images })

def preprocess_json(json_string):
    """
    Converts Python-style values in a JSON string (None, True, False) to JSON-compatible values (null, true, false).
    
    Args:
    - json_string (str): The raw JSON string.
    
    Returns:
    - str: The processed JSON string.
    """
    # Replace Python-style None, True, False with JSON-compatible null, true, false
    json_string = re.sub(r"\bNone\b", "null", json_string)
    json_string = re.sub(r"\bTrue\b", "true", json_string)
    json_string = re.sub(r"\bFalse\b", "false", json_string)
    
    # pd read csv fix for if AI says filepath instead of filepath_or_buffer
    json_string = re.sub(r"\bfilepath\b", "filepath_or_buffer", json_string)
    
    return json_string

def validate_ai_response(ai_response):
    """
    Validate the AI's JSON response according to the given rules.

    Args:
    - ai_response (str): The JSON string returned by the AI.
    
    Returns:
    - tuple: (reason, is_valid) where reason explains the validation failure OR just answer type (START, FORMAT, ERROR), 
             and is_valid is True or False.
    """
    try:
        # Parse the JSON string into a dictionary
        response = json.loads(ai_response)
    except json.JSONDecodeError:
        return ("JSONDecodeError - Invalid JSON format.", False)

    # Extract "Next" field to determine the type of response
    answer_type = response.get("Next")

    if answer_type == "START":
        # Validate "START" format
        for key, value in response.items():
            if key == "Next":
                continue

            if not isinstance(value, dict): 
                return (f"Error validating JSON - Value '{value}' should be of type dict but got: {type(value)}.", False)
                
            if "function" not in value:
                return (f"Error validating JSON - Required 'function' key not found in {value}.", False)
            
            if "parameters" not in value:
                return (f"Error validating JSON - Required 'parameters' key not found in {value}.", False)

            function_name = value["function"]

            # Check if the function is prefixed or is a built-in
            if not any(function_name.startswith(prefix) for prefix in ALLOWED_PREFIXES) and function_name.split("(")[0] not in ALLOWED_BUILT_INS:
                return (f"Invalid function '{function_name}' - Must be prefixed by {ALLOWED_PREFIXES} or be a built-in Python function.", False)

            # Ensure parameters is a dictionary
            if not isinstance(value["parameters"], dict):
                return (f"Error validating JSON - Parameters for '{key}' should be a dict but got {type(value['parameters'])}.", False)

    elif answer_type == "ERROR":
        # Validate "ERROR" format
        if "Reason" not in response:
            return ("Error validating JSON - Missing required 'Reason' key in 'ERROR' response type.", False)

    elif answer_type == "FORMAT":
        # Validate "FORMAT" format
        if "Formatted" not in response:
            return ("Error validating JSON - Missing 'Formatted' key in 'FORMAT' response type.", False)

    else:
        # Invalid "Next" value
        return (f"INVALID_NEXT - Invalid 'Next' value '{answer_type}'. Expected: 'START', 'ERROR', or 'FORMAT'.", False)

    return (answer_type, True)

def execute_agent_instructions(instructions, plot_save_path):
    """
    Execute the Python, Pandas, Numpy, and Matplotlib functions provided in the instructions.
    
    Args:
    - instructions (dict): Dictionary of function calls and parameters.
    - plot_save_path (str): Path where the plot PNG will be saved if the last function is a plot.
    
    Returns:
    - tuple: (results, isPlot) where results is just a list of results and isPlot tells you if the last function resulted in a plot being saved.
    """
    # Keep track of intermediate results to allow referencing "RESULTX"
    results = {}

    for key, step in instructions.items():
        if key == "Next":  # Skip the "Next" field
            continue

        function_name = step["function"]  # e.g., "pd.read_csv"
        parameters = step["parameters"]  # e.g., { "filepath_or_buffer": "results.csv" }

        # Parse module and function name (e.g., "pd.read_csv")
        module_name, func_name = function_name.split(".")[0], function_name.split(".")[1]

        # Import the appropriate module (pandas, numpy, matplotlib, etc.)
        module = globals().get(module_name)
        if not module:
            raise ImportError(f"Module {module_name} not found. Ensure the module is imported.")

        # Resolve parameters (handle references like "RESULTX['column_name']")
        resolved_params = {}
        for param_name, param_value in parameters.items():
            if isinstance(param_value, str) and "RESULT" in param_value:
                # Check if it's a reference to the entire DataFrame or a specific column
                if "[" in param_value:
                    result_ref, column = param_value.split("[")
                    result_key = result_ref.strip()  # e.g., "RESULT1"
                    column_name = column.strip("']")
                    resolved_params[param_name] = results[result_key][column_name]  # Specific column
                else:
                    resolved_params[param_name] = results[param_value.strip()]  # Entire DataFrame
            elif param_name == "filepath_or_buffer" and func_name == "read_csv":
                # Prepend base path for read_csv
                if not os.path.isabs(param_value):
                    param_value = os.path.join(BASE_UPLOAD_PATH, param_value)
                resolved_params[param_name] = param_value
            else:
                resolved_params[param_name] = param_value

        # Call the function dynamically
        func = getattr(module, func_name)

        if function_name == "plt.show":
            # Skip plt.show() and save the plot instead
            plt.savefig(plot_save_path, bbox_inches="tight")
            time.sleep(1)
            print(f"Plot saved as {plot_save_path}")
            plt.close()  # Close the plot to avoid overlapping
            return f"""
            <img src='{os.path.relpath(plot_save_path, "page")}'>
            <br>
            <a href="{os.path.relpath(plot_save_path, "page")}" download="{os.path.relpath(plot_save_path, "page")}">
                <button class='download_button'>
                    <i class="fa-solid fa-download"></i>
                </button>
            </a>
            """, True
        else:
            result = func(**resolved_params)
            if result is not None:
                results[key] = result  # Store the result for future steps

    return results, False

if __name__ == "__main__":
    socketio.run(app, debug=True)