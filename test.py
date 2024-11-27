###########################################
### Test script, outdated at the moment ###
###########################################


# TODO: Update this script to work with the new structure


from dotenv import load_dotenv
from functions import *
from helpers import *
import pandas as pd
import json

load_dotenv()

# Example JSON result
result_json = '''
{
    "RESULT1": {
        "function": "plot_bar_chart",
        "parameters": {
            "data": {
                "Budget": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 18.0, 19.0, 25.0],
                "AP": [5030, 8578, 26086, 1574, 8492, 18214, 6054, 22342, 25513, 3451, 24561, 1326, 32414, 7552]
            },
            "column_x": "Budget",
            "column_y": "AP"
        }
    }
}
'''

# Load JSON
results = json.loads(result_json)

# Load the data
data = pd.read_csv("dummy_data.csv")

# Storage for intermediate results
computed_results = {}

# Process each result in the JSON
for key, value in results.items():
    func_name = value["function"]
    params = value["parameters"]
    
    # Replace references to previous results
    for param_key, param_value in params.items():
        if isinstance(param_value, list):  # For arrays
            params[param_key] = [computed_results[item] for item in param_value]
        elif isinstance(param_value, str) and param_value.startswith("RESULT"):
            params[param_key] = computed_results[param_value]
    
    # Add data if needed
    if "data" in params:
        if params["data"] == "dummy_data.csv":
            params["data"] = data
        if isinstance(params["data"], dict):
            params["data"] = pd.DataFrame(params["data"])
    
    # Call the function
    computed_results[key] = function_map[func_name](**params)

# Final result
final_key = list(computed_results.keys())[-1]
final_result = computed_results[final_key]

# New prompt
new_prompt = f"""
    Below you will receive the result of your answer. Please return one of the following:
    1. FORMAT - if the answer is fine to return to the user. Please make sure to format the answer to make it readable.
    Return it in the following format:
    {{
        "Next": "FORMAT",
        "Formatted": "formatted_answer"
    }}
    
    2. ADJUST - if you need to make some further adjustments with the given functions.
    Return it in the following format, make sure to enter the next # for RESULT:
    {{
        "Next": "ADJUST",
        "RESULT#": {{
            "function": "function_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
    }}
    
    3. RETRY - if you need to start over with the given functions.
    Return it in this format:
    {{
        "Next": "RETRY",
        "RESULT1": {{
            "function": "function_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
    }}
    
    ---
    Result: {final_result}
"""
#print(new_prompt)