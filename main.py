###########################################
### Main script for prompting the model ###
###########################################


# TODO: Improve prompts and prompt handling to minimize token usage
# TODO: Ensure as little as possible is handled in this script


from functions import function_map
from helpers import prompt_model
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import os

load_dotenv()

def main(model):
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
    system = f"""
    Instructions:
    1. You will receive a list of available functions, information about the data, and a question posed by the user. Determine which function(s) to call to answer this question, using the available information. These functions will be applied in the specified order.
    2. Ensure that each function, except the last, is used in any subsequent function. The result of the last function will be returned to the user.
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
        ...
    }}
    4. If no valid function applies, return:
    {{
        'Next': 'ERROR'
    }}
    5. DO NOT add comments or other code to the template.
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
    """

    init_prompt = f"""
    Data file name: {file_name}
    Number of rows: {data.shape[0]}
    Column info: {column_info}
    ---
    User Question:
    {user_question}
    """
    
    result_prompt = f"""
    Below is the final result of your answer. Please return one of the following:
    1. FORMAT - if the answer is fine to return to the user. Please make sure to format the answer to make it readable.
    Return it in the following format:
    {{
        "Next": "FORMAT",
        "Formatted": "formatted_answer"
    }}
    2. START - if the result does not answer the question and you need to start over with the given functions.
    Return the format you received in the initial prompt.
    ---
    """

    follow_up_prompt = f"""
    The user has asked a follow-up question. Please make sure to stick to the original instructions.
    ---
    """

    retry_prompt = f"""
    An error occurred when implementing the given funtions. Please rethink your answer and try SOMETHING DIFFERENT.
    ---
    """

    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("API_KEY"))
    conversation_history = [
        {"role": "system", "content": system}
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
        elif prompt_type == 'stop':
            print("Quitting...")
            return
        prompt_type = 'result'
        conversation_history.append(user_prompt)
        
        # Dev check
        print(user_prompt["content"])
        if input(f"\nEnter Y to continue\n") != "Y":
            print("Quitting...")
            return

        answered, prompt_type, result = prompt_model(client, conversation_history, data, function_map, model)

if __name__ == '__main__':
    main("gpt-4o-mini")
