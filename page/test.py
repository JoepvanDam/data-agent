import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json
import os

BASE_UPLOAD_PATH = "page/uploads"  # Add your base path here


def execute_agent_instructions(instructions, plot_save_path="plot.png"):
    """
    Execute the Python, Pandas, Numpy, and Matplotlib functions provided in the instructions.
    
    Args:
    - instructions (dict): Dictionary of function calls and parameters.
    - plot_save_path (str): Path where the plot PNG will be saved if the last function is a plot.
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
            print(f"Plot saved as {plot_save_path}")
            plt.close()  # Close the plot to avoid overlapping
        else:
            result = func(**resolved_params)
            if result is not None:
                results[key] = result  # Store the result for future steps

    return results

# Example usage:
if __name__ == "__main__":
    # Example JSON instructions
    instructions_json = '''
    {
    "Next": "START",
    "RESULT1": { "function": "pd.read_csv", "parameters": { "filepath_or_buffer": "results.csv" } },
    "RESULT2": { "function": "sns.set_style", "parameters": { "style": "whitegrid" } },
    "RESULT3": {
        "function": "sns.lmplot",
        "parameters": {
        "x": "Input_size",
        "y": "Output_size",
        "data": "RESULT1",
        "hue": "Model",
        "height": 6,
        "aspect": 1.5,
        "scatter_kws": { "s": 50, "alpha": 0.7 },
        "line_kws": { "linewidth": 2, "alpha": 0.8 },
        "fit_reg": false
        }
    },
    "RESULT4": { "function": "plt.xlabel", "parameters": { "xlabel": "Input Size" } },
    "RESULT5": { "function": "plt.ylabel", "parameters": { "ylabel": "Output Size" } },
    "RESULT6": { "function": "plt.title", "parameters": { "label": "Scatter Plot with Faceted Models (Input Size vs Output Size)" } },
    "RESULT7": { "function": "plt.show", "parameters": {} }
    }
    '''
    instructions = json.loads(instructions_json)

    # Run the instructions and save the plot as "output_plot.png"
    execute_agent_instructions(instructions, plot_save_path="output_plot.png")
