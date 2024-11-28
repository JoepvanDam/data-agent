###################
### Test script ###
###################

from helpers import run_functions
import pandas as pd

test_prompt = """{ "Next": "START", "RESULT1": { "function": "custom_table", "parameters": { "data": "data", "columns": ["AP", "SP"], "filters": {} } }, "RESULT2": { "function": "correlation_matrix", "parameters": { "data": "RESULT1" } } }"""

data = pd.read_csv('dummy_data.csv')
status, prompt_type, result = run_functions(test_prompt, data)
print(status)
print(prompt_type)
print(result)