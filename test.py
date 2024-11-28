###################
### Test script ###
###################

from helpers import run_functions
import pandas as pd

test_prompt = """{ "Next": "START", "RESULT1": { "function": "grouped_summary", "parameters": { "data": "dummy_data.csv", "group_by_column": "Prov", "agg_column": "Budget", "agg_func": "mean" } }, "RESULT2": { "function": "dict_to_df", "parameters": { "dict": "RESULT1", "column_names": ["Prov", "AverageBudget"] } }, "RESULT3": { "function": "plot_histogram", "parameters": { "data": "RESULT2", "column": "AverageBudget", "bins": 10 } } }"""

data = pd.read_csv('dummy_data.csv')
status, prompt_type, result = run_functions(test_prompt, data)
print(status)
print(prompt_type)
print(result)