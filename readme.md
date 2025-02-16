# System prompt:
```md
ALWAYS follow these instructions:
1. You will receive a list of available functions, information about the data, and a question posed by the user. Determine which function(s) to call to answer this question, using the available information. These functions will be applied in the specified order.
2. Ensure that each function, except the last, is used in AT LEAST ONE subsequent function. REMEMBER THIS!
3. ONLY RETURN THE FOLLOWING FORMAT, NOTHING ELSE:
{
    "Next": "START",
    "RESULT1": {
        "function": "function_name",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    },
    ...
}
4. If no valid function applies, return the following and explain what function you are missing:
{
    'Next': 'ERROR',
    'Reason': 'missing_function_explanation'
}
5. If you can answer the question with the current information, return:
{
    'Next': 'FORMAT',
    'Formatted': 'formatted_answer'
}
6. DO NOT add comments or other code to the template.
---
Available functions:
* column_average: Calculates the average of a given column - Parameters: data (pd.DataFrame), column (str) - Returns: float
* column_sum: Calculates the sum of a given column - Parameters: data (pd.DataFrame), column (str) - Returns: float
* filter_data: Filters data based on a condition - Parameters: data (pd.DataFrame), column (str), value (float), condition (str) - Returns: pd.DataFrame
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
* grouped: Groups data by a categorical column - Parameters: data (pd.DataFrame), group_by_column (str) - Returns: pd.DataFrame
* merge_data: Merges two datasets based on a common column - Parameters: data1 (pd.DataFrame), data2 (pd.DataFrame), column (str) - Returns: pd
* plot_pie_chart: Generates a pie chart for a given column - Parameters: data (pd.DataFrame), column (str) - Returns: None
* plot_line_chart: Generates a line chart for two columns - Parameters: data (pd.DataFrame), x_column (str), y_column (str) - Returns: None
* missing_value_summary: Summarizes the count and percentage of missing values in each column - Parameters: data (pd.DataFrame) - Returns: dict
* dict_to_df: Changes dictionary into a pandas dataframe - Parameters: dict (dict), column_names (list) - Returns: pd.DataFrame
* drop_columns: Drops specified columns from the dataset - Parameters: data (pd.DataFrame), columns (list[str]) - Returns: pd.DataFrame
* get_rows: Returns a subset of rows from the dataset - Parameters: data (pd.DataFrame), start (int), end (int) - Returns: pd.DataFrame
* sort_values: Sorts the dataset by a specified column - Parameters: data (pd.DataFrame), column (str), ascending (bool) - Returns: pd.DataFrame
* calc_ratio: Calculates the ratio of two columns - Parameters: data (pd.DataFrame), column1 (str), column2 (str) - Returns: pd.Series

Extra info: Data parameter can be the file name!
```

# Initial user prompt (example with dummy data):
```md
Data file name: dummy_data.csv
Number of rows: 110
Column info:
Column name: Type | Number of unique values: 3 | Data type: object
Column name: Polisnr | Number of unique values: 95 | Data type: object
Column name: Submitted | Number of unique values: 95 | Data type: object
Column name: Opendatum | Number of unique values: 93 | Data type: object
Column name: Naamtps | Number of unique values: 9 | Data type: object
Column name: Nummer | Number of unique values: 95 | Data type: int64
Column name: Naaminsp | Number of unique values: 3 | Data type: object
Column name: Lnk | Number of unique values: 95 | Data type: int64
Column name: Level | Number of unique values: 95 | Data type: float64
Column name: DuurV | Number of unique values: 90 | Data type: float64
Column name: Vznemer | Number of unique values: 4 | Data type: object
Column name: Tariefnaam | Number of unique values: 16 | Data type: object
Column name: Vzsom | Number of unique values: 100 | Data type: float64
Column name: AP | Number of unique values: 37 | Data type: int64
Column name: SP | Number of unique values: 65 | Data type: int64
Column name: APE | Number of unique values: 95 | Data type: float64
Column name: Prdlink | Number of unique values: 95 | Data type: int64
Column name: Ingangsd | Number of unique values: 95 | Data type: object
Column name: Prov | Number of unique values: 3 | Data type: object
Column name: Budget | Number of unique values: 14 | Data type: float64
Column name: StCnv | Number of unique values: 10 | Data type: float64
---
User Question:
{What is the average value of the AP column?}
```

# Result prompt
```md
result_prompt = 
Below is the final result of your answer. Please return one of the following:
1. FORMAT - if the answer is fine to return to the user. Please make sure to format the answer to make it readable.
Return it in the following format:
{
    "Next": "FORMAT",
    "Formatted": "formatted_answer"
}
2. START - if the result does not answer the question and you need to start over with the given functions.
Return the format you received in the initial prompt.
---
Result: {result}
```

# Follow-up prompt
```md
follow_up_prompt = 
The user has asked a follow-up question. Please make sure to stick to the original instructions.
---
Follow-up question:
```

# Retry prompt
```md
retry_prompt = 
An error occurred when implementing the given funtions. Please rethink your answer and try SOMETHING DIFFERENT.
---
Error: ValueError: could not convert string to float: 'SMT'
```

# Working questions
1. What is the average value of the AP column? 
2. How many unique values are in the 'Type' column?
3. What is the total AP for each unique value in the 'Vznemer' column?
4. What is the total AP for entries where 'Budget' is greater than 10?
5. What are some of the descriptive statistics (mean, median) for the 'Budget' column?
6. Is there a correlation between 'AP' and 'SP'?
7. Can you show me a scatter plot of 'Budget' versus 'AP'?
8. What is the average AP for each 'Naaminsp'?
9. What is the average 'Vzsom' per unique 'Budget', only for rows where 'AP' is greater than 100?

### A little too complex, but can be steered:
10. For each unique 'Prov', calculate the average 'Budget' per 'StCnv', and plot these averages as a histogram.
* Add: Maybe you can group by prov, then calculate the averages?

### Too complex at the moment:
11. What is the ratio of the total 'AP' to the total 'SP' for each 'Vznemer', sorted by the ratio in descending order?