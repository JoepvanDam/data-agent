import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI
import seaborn as sns
import pandas as pd
import matplotlib
import json
import os

matplotlib.use("QtAgg")
load_dotenv()

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

def dict_to_df(dict):
    return pd.DataFrame([dict])

# Dict checker helper function
def validate_dict(dict):
    results = {key: value for key, value in dict.items() if key.startswith("RESULT")}
    result_keys = sorted(results.keys())
    total_results = len(result_keys)

    # Check 1: Plot function not being the last item
    for i, key in enumerate(result_keys):
        if i < total_results - 1:
            function_name = results[key]['function']
            if function_name.startswith("plot_"):
                return f"Error: '{function_name}' in {key} is a plot function but not the last RESULT item."

    # Check 2: Ensure past RESULT1, previous RESULT#s are used
    for i in range(1, total_results):
        current_key = result_keys[i]
        current_params = results[current_key]['parameters']
        previous_keys = result_keys[:i]

        # Check if any previous RESULT# is referenced in current parameters
        references_previous = any(
            prev_key in str(current_params) for prev_key in previous_keys
        )

        if not references_previous:
            return f"Error: {current_key} does not reference any previous RESULT#."
    return "Valid"

def main():
    # Read data
    file_name = 'dummy_data.csv'
    data = pd.read_csv(file_name)

    # Get data info
    column_info = ""
    for col in data.columns:
        column_info += f"Column name: {col} | "
        column_info += f"Number of unique values: {data[col].nunique()} | "
        column_info += f"Data type: {data[col].dtype}\n"

    # Get user question
    user_question = input('What is your question? ')

    # Prompts
    init_prompt = f"""
    Instructions:
    1. Below you will receive a list of available functions, information about the data, and the user question. Determine which function(s) to call based on the user's question. These functions will be applied in the specified order.
    2. ALWAYS ensure that all functions past the first use a previous function as a parameter!!!
    3. ONLY RETURN THE FOLLOWING FORMAT, NOTHING ELSE:
    {{
        "Next": "START",
        "RESULT1": {{
            "function": "function_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }},
        "RESULT2": {{
            "function": "function_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }},
        ...
    }}
    4. DO NOT add comments or other code to this template.
    
    ---
    Available functions:
    * column_average: Calculates the average of a given column - Parameters: data (pd.DataFrame), column (str) - Returns: float
    * column_sum: Calculates the sum of a given column - Parameters: data (pd.DataFrame), column (str) - Returns: float
    * divide: Divides num1 by num2 - Parameters: num1 (float), num2 (float) - Returns: float
    * multiply: Multiplies num1 by num2 - Parameters: num1 (float), num2 (float) - Returns: float
    * add: Adds all numbers in the array together in order - Parameters: num_array (list[float]) - Returns: float
    * subtract: Subtracts all numbers in the array from each other in order - Parameters: num_array (list[float]) - Returns: float
    * describe_column: Generates descriptive statistics for a specific column - Parameters: data (pd.DataFrame), column (str) - Returns: dict
    * value_counts: Counts the occurrences of each unique value in a column - Parameters: data (pd.DataFrame), column (str) - Returns: dict
    * plot_bar_chart: Generates a bar chart for two numerical columns - Parameters: data (pd.DataFrame), column_x (str), column_y (str) - Returns: None
    * plot_scatter_plot: Generates a scatter plot for two numerical columns - Parameters: data (pd.DataFrame), column_x (str), column_y (str) - Returns: None
    * plot_histogram: Generates a histogram for a numerical column - Parameters: data (pd.DataFrame), column (str), bins (int) - Returns: None
    * plot_boxplot: Creates a boxplot for a numerical column - Parameters: data (pd.DataFrame), column (str) - Returns: None
    * correlation_matrix: Generates a correlation matrix for numerical columns - Parameters: data (pd.DataFrame) - Returns: dict
    * plot_correlation_heatmap: Plots a heatmap for the correlation matrix of numerical columns - Parameters: data (pd.DataFrame) - Returns: None
    * generate_summary_table: Generates a summary table for the dataset - Parameters: data (pd.DataFrame) - Returns: dict
    * grouped_summary: Groups data by a categorical column and applies an aggregation function to another column - Parameters: data (pd.DataFrame), group_by_column (str), agg_column (str), agg_func (str) - Returns: dict
    * plot_pie_chart: Generates a pie chart for a given column - Parameters: data (pd.DataFrame), column (str) - Returns: None
    * plot_line_chart: Generates a line chart for two columns - Parameters: data (pd.DataFrame), x_column (str), y_column (str) - Returns: None
    * missing_value_summary: Summarizes the count and percentage of missing values in each column - Parameters: data (pd.DataFrame) - Returns: dict
    * custom_table: Filters data and returns a specific set of columns - Parameters: data (pd.DataFrame), columns (list[str]), filters (dict) - Returns: list[dict]
    * dict_to_df: Changes dictionary into a pandas dataframe - Parameters: dict (dict) - Returns: pd.DataFrame
    
    ---
    Data file name: {file_name}
    Number of rows: {data.shape[0]}
    Column info: {column_info}

    ---
    User Question:
    {user_question}
    """
    
    result_prompt = f"""
    Below you will receive the result of your answer. Please return one of the following:
    1. FORMAT - if the answer is fine to return to the user. Please make sure to format the answer to make it readable.
    Return it in the following format:
    {{
        "Next": "FORMAT",
        "Formatted": "formatted_answer"
    }}
    
    2. START - if you need to start over with the given functions.
    Return it in this format:
    {{
        "Next": "START",
        "RESULT1": {{
            "function": "function_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
    }}
    
    ---
    """

    follow_up_prompt = f"""
    The user has asked a follow-up question, which will be shown below. Please make sure to stick to the original instructions.
    
    ---
    """

    retry_prompt = f"""
    An error occurred when implementing the given funtions. Please rethink your answer and try SOMETHING DIFFERENT.
    
    ---
    """

    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("API_KEY"))
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    # Initial user prompt
    user_prompt = {"role": "user", "content": init_prompt}
    conversation_history.append(user_prompt)
    
    prompt_type = 'init'
    answered = False
    result = None
    while not answered:
        if prompt_type == "init":
            user_prompt = {"role": "user", "content": init_prompt}
        elif prompt_type == "result":
            user_prompt = {"role": "user", "content": result_prompt + f"Result: {result}"}
        elif prompt_type == "follow_up":
            user_prompt = {"role": "user", "content": follow_up_prompt + f"Follow-up question: {result}"}
        elif prompt_type == 'retry':
            user_prompt = {"role": "user", "content": retry_prompt + f"Error: {result}"}
        prompt_type = 'result'
        conversation_history.append(user_prompt)
        
        # Dev check
        print(user_prompt["content"])
        if input(f"\nEnter Y to continue\n") != "Y":
            print("Quitting...")
            return

        # Create a chat completion
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model="gpt-4o-mini",
        )

        # Extract and print only the assistant's response
        assistant_response = chat_completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_response})
        print("\nResponse:\n", assistant_response, "\nNow running functions...")
        
        try:
            # Load JSON
            results = json.loads(assistant_response)
            
            # Check validity and next type
            validity = validate_dict(results)
            if validity != "Valid":
                prompt_type = 'retry'
                result = validity
            elif results['Next'] == "START": # Start from nothing
                # Remove next type
                results.pop('Next', None)
                
                # Storage for intermediate results
                computed_results = {}
                
                # Define function map
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
                    "custom_table": custom_table,
                    "dict_to_df": dict_to_df
                }

                # Process each result in the JSON
                for key, value in results.items():
                    func_name = value["function"]
                    params = value["parameters"]
                    
                    # Replace references to previous results
                    for param_key, param_value in params.items():
                        if isinstance(param_value, list):
                            params[param_key] = [computed_results[item] for item in param_value]
                        elif isinstance(param_value, str) and param_value.startswith("RESULT"):
                            params[param_key] = computed_results[param_value]
                    
                    # Add data if needed
                    if "data" in params and params["data"] == "dummy_data.csv":
                        params["data"] = data
                    
                    # Call the function
                    computed_results[key] = function_map[func_name](**params)

                # Result
                key = list(computed_results.keys())[-1]
                result = computed_results[key]
            elif results['Next'] == 'FORMAT': # Print the formatted result
                prompt_type = 'follow_up'
                print(results['Formatted'])
                result = input("\nWould you like to ask another question?\n")
            else: # ERROR (currently for testing, should be implemented as an actual error in the future)
                prompt_type = 'retry'
                result = f"Unknown 'Next' element: {results['next']}. Valid options include: FORMAT or START"
        except Exception as e:
            print(e)
            prompt_type = 'retry'
            result = e

if __name__ == '__main__':
    main()
