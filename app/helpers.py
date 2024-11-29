#######################################################################################
### Script with helper functions for prompting the model and validating the prompts ###
#######################################################################################


# TODO: Add testing options for prompting:
# 1. How long the model takes to respond # DONE
# 2. How many prompts are needed to get the final result DONE
# 3. How many errors occur during the process and what they are


from functions import function_map
import pandas as pd
import traceback
import tiktoken
import json
import time

# Dict checker helper function
def validate_dict(dict):
    """
    Validate the dictionary containing the functions to run.

    Parameters:
    dict (dict): The dictionary containing the functions to run.

    Returns:
    str: A string indicating whether the dictionary is valid or an error message.
    """
    results = {key: value for key, value in dict.items() if key.startswith("RESULT")}
    result_keys = sorted(results.keys())
    total_results = len(result_keys)

    # Check 1: Plot function not being the last item
    for i, key in enumerate(result_keys):
        if i < total_results - 1:
            function_name = results[key]['function']
            if function_name.startswith("plot_"):
                return f"Error: '{function_name}' in {key} is a plot function but not the last RESULT item."

    # Check 2: Ensure every RESULT item has a function and parameters
    for key, value in results.items():
        if 'function' not in value or 'parameters' not in value:
            return f"Error: Missing 'function' or 'parameters' in {key}."
        
    # Check 3: Ensure all functions are valid
    valid_functions = [key for key in function_map.keys()]
    for key, value in results.items():
        if value['function'] not in valid_functions:
            return f"Error: Invalid function '{value['function']}' in {key}."
        
    # Check 4: Ensure every RESULT item is used in a subsequent function, except the last one
    for i, key in enumerate(result_keys):
        if i < total_results - 1:
            used = False
            for _, value in results.items():
                for param in value['parameters'].values():
                    if isinstance(param, str) and param == key:
                        used = True
            if not used:
                return f"Error: {key} is not used in a subsequent function."
    return "Valid"

# Run functions helper function
def run_functions(assistant_response, data):
    """
    Run the functions defined in the JSON results and return the final result.

    Parameters:
        assistant_response (str): The response from the assistant.

    Returns:
        tuple: A tuple containing the status of the function, the prompt type, and the result of the function.
    """
    # Load JSON
    results = json.loads(assistant_response)
    
    # Check validity and next type
    validity = validate_dict(results)
    if validity != "Valid": # Invalid function (retry)
        prompt_type = 'retry'
        result = validity
        return 'error', prompt_type, result
    elif results['Next'] == "ERROR": # No valid functions available (return)
        return 'stop', "No valid function found to answer the question, please try again.", None
    elif results['Next'] == "START": # Start from nothing (init)
        # Remove next type
        results.pop('Next', None)
        
        # Storage for intermediate results
        computed_results = {}

        # Process each result in the JSON
        for key, value in results.items():
            func_name = value["function"]
            params = value["parameters"]
            
            # Replace references to previous results
            for param_key, param_value in params.items():
                if isinstance(param_value, list) and all(isinstance(item, str) and item.startswith("RESULT") for item in param_value):
                    params[param_key] = [computed_results[item] for item in param_value]
                elif isinstance(param_value, str) and param_value.startswith("RESULT"):
                    params[param_key] = computed_results[param_value]
            
            # Add data if needed
            if "data" in params and isinstance(params["data"], str):
                if params["data"].endswith(".csv"):
                    data = pd.read_csv(f"{params['data']}")
                    params["data"] = data
                elif params["data"] == "data":
                    params["data"] = data
                
            # Turn strings into numbers if needed
            for param_key, param_value in params.items():
                if isinstance(param_value, str) and param_value.isdigit():
                    params[param_key] = int(param_value)
               
            # Call the function
            computed_results[key] = function_map[func_name](**params)

        # Result
        key = list(computed_results.keys())[-1]
        result = computed_results[key]
        return 'format', 'result', result
    elif results['Next'] == 'FORMAT': # Print the formatted result (follow-up) - currently not implemented
        prompt_type = 'follow_up'
        print(results['Formatted'])
        return 'stop', 'stop', None
    else: # Currently for testing, should be implemented as an actual error in the future (retry)
        prompt_type = 'retry'
        result = f"Unknown 'Next' element: {results['Next']}. Valid options include: ERROR, FORMAT or START"
        return 'error', prompt_type, result

# Count tokens helper function
def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Prompt function
def prompt_model(client, conversation_history, model, data, test=False):
    """
    Prompt the OpenAI model with the conversation history and process the response.

    Parameters:
        client (openai.ChatCompletion): The OpenAI ChatCompletion client.
        conversation_history (list): The conversation history with the user and assistant.
        data (pd.DataFrame): The data to be used in the functions.
        function_map (dict): A dictionary mapping function names to their implementations.

    Returns:
        tuple: A tuple containing a boolean indicating whether the function ran successfully, the prompt type, and
        the result of the function.
    """
    answered = False

    # Call model
    if test:
        start_time = time.time()
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
        )
        end_time = time.time()
        response_time = end_time - start_time
        print(f"\nResponse time: {response_time} seconds \\")

        # Count input tokens
        in_token_count = 0
        for message in conversation_history:
            in_token_count += num_tokens_from_string(message['content'], model)
        print(f"In tokens used: {in_token_count} \\")
    else:
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
        )

    # Extract assistant's response
    assistant_response = chat_completion.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_response})
    

    # Count output tokens
    if test:
        out_token_count = num_tokens_from_string(assistant_response, model)
        print(f"Out tokens used: {out_token_count}")
    
    print("\nResponse:\n", assistant_response)
    
    try:
        status, prompt_type, result = run_functions(assistant_response, data) # Status can be: 'result', 'stop', 'error', 'follow_up'
        if status == 'result' or status == 'error':
            return False, prompt_type, result
        elif status == 'stop':
            return True, prompt_type, result
    except Exception as e:
        print(e)
        traceback.print_exc()
        prompt_type = 'retry'
        result = e
    return answered, prompt_type, result