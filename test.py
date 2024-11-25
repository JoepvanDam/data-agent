import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib
import json

matplotlib.use("QtAgg")

# All functions
def column_average(data, column):
    return data[column].mean()

def column_sum(data, column):
    return data[column].sum()

def divide(num1, num2):
    return num1 / num2

def multiply(num1, num2):
    return num1 * num2

def add(num_array):
    return sum(num_array)

def subtract(num_array):
    result = num_array[0]
    for num in num_array[1:]:
        result -= num
    return result

def describe_column(data, column):
    return data[column].describe().to_dict()

def value_counts(data, column):
    return data[column].value_counts().to_dict()

def plot_bar_chart(data, column_x, column_y):
    data.plot.bar(x=column_x, y=column_y)
    plt.title(f"Bar Chart: {column_x} vs {column_y}")
    plt.xlabel(column_x)
    plt.ylabel(column_y)
    plt.show()

def plot_scatter_plot(data, column_x, column_y):
    data.plot.scatter(x=column_x, y=column_y)
    plt.title(f"Scatter Plot: {column_x} vs {column_y}")
    plt.xlabel(column_x)
    plt.ylabel(column_y)
    plt.show()

def plot_histogram(data, column, bins=10):
    data[column].plot(kind='hist', bins=bins)
    plt.title(f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.show()

def plot_boxplot(data, column):
    data.boxplot(column=[column])
    plt.title(f"Boxplot of {column}")
    plt.show()

def correlation_matrix(data):
    return data.corr().to_dict()

def plot_correlation_heatmap(data):
    corr = data.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.show()

def generate_summary_table(data):
    summary = data.describe(include='all').transpose()
    return summary.to_dict()

def grouped_summary(data, group_by_column, agg_column, agg_func):
    return data.groupby(group_by_column)[agg_column].agg(agg_func).to_dict()

def plot_pie_chart(data, column):
    value_counts = data[column].value_counts()
    value_counts.plot(kind='pie', autopct='%1.1f%%')
    plt.title(f"Pie Chart of {column}")
    plt.ylabel("")
    plt.show()

def plot_line_chart(data, x_column, y_column):
    data.plot(x=x_column, y=y_column, kind='line')
    plt.title(f"Line Chart: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.show()

def missing_value_summary(data):
    missing_values = data.isnull().sum()
    total_rows = len(data)
    return {
        column: {
            "missing_count": count,
            "missing_percentage": (count / total_rows) * 100
        }
        for column, count in missing_values.items()
    }

def custom_table(data, columns, filters=None):
    if filters:
        for column, value in filters.items():
            data = data[data[column] == value]
    return data[columns].to_dict(orient="records")

function_map = {
    "column_average": column_average,
    "column_sum": column_sum,
    "divide": divide,
    "multiply": multiply,
    "add": add,
    "subtract": subtract,
    "describe_column": describe_column,
    "value_counts": value_counts,
    "plot_bar_chart": plot_bar_chart,
    "plot_scatter_plot": plot_scatter_plot,
    "plot_histogram": plot_histogram,
    "plot_boxplot": plot_boxplot,
    "correlation_matrix": correlation_matrix,
    "plot_correlation_heatmap": plot_correlation_heatmap,
    "generate_summary_table": generate_summary_table,
    "grouped_summary": grouped_summary,
    "plot_pie_chart": plot_pie_chart,
    "plot_line_chart": plot_line_chart,
    "missing_value_summary": missing_value_summary,
    "custom_table": custom_table
}

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