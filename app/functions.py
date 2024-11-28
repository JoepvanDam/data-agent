########################################################
### Script with all functions that the model can use ###
########################################################


# TODO: Add more functions to the function_map
# TODO: Make function map automatically generated (if possible)


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib

matplotlib.use("QtAgg")

# All functions
def column_average(data, column):
    return data[column].mean()

def column_sum(data, column):
    return data[column].sum()

def column_correlation(data, column1, column2):
    return data[column1].corr(data[column2])

def filter_data(data, column, value, condition):
    if condition == ">" or condition == "greater":
        return data[data[column] > value]
    elif condition == "<" or condition == "less":
        return data[data[column] < value]
    elif condition == ">=" or condition == "greater_equal":
        return data[data[column] >= value]
    elif condition == "<=" or condition == "less_equal":
        return data[data[column] <= value]
    elif condition == "==" or condition == "equal":
        return data[data[column] == value]
    elif condition == "!=" or condition == "not_equal":
        return data[data[column] != value]

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

def grouped(data, group_by_column, agg_column):
    return data.groupby(group_by_column)[agg_column]

def merge_data(data1, data2, on, how):
    return data1.merge(data2, on=on, how=how)

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

def dict_to_df(dict, column_names):
    df = pd.DataFrame(list(dict.items()), columns=column_names)
    return df

def drop_columns(data, columns):
    return data.drop(columns=columns)

def get_rows(data, start, end):
    return data.iloc[start:end]

def sort_values(data, column, ascending):
    return data.sort_values(by=column, ascending=ascending)

function_map = {
    "column_average": column_average,
    "column_sum": column_sum,
    "column_correlation": column_correlation,
    "filter_data": filter_data,
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
    "grouped": grouped,
    "merge_data": merge_data,
    "plot_pie_chart": plot_pie_chart,
    "plot_line_chart": plot_line_chart,
    "missing_value_summary": missing_value_summary,
    "dict_to_df": dict_to_df,
    "drop_columns": drop_columns,
    "get_rows": get_rows,
    "sort_values": sort_values
}