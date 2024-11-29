import pandas as pd

def calculate_cost(caching, runs, error_rate, model="gpt-4o-mini"):
    # Constants
    if model == "gpt-4o":
        CACHE_MULTIPLIER = 0.00125 if caching else 0.0025
    elif model == "gpt-4o-mini":
        CACHE_MULTIPLIER = 0.000075 if caching else 0.00015
    elif model == "o1-preview":
        CACHE_MULTIPLIER = 0.0075 if caching else 0.015
    elif model == "o1-mini":
        CACHE_MULTIPLIER = 0.0015 if caching else 0.003
    else:
        raise ValueError(f"Unknown model: {model}")

    SYSTEM_PROMPT_COST = 1155 / 1000
    QUESTION_COST = 500 / 1000
    FORMAT_COST = 150 / 1000
    ERROR_COST = 100 / 1000

    # Calculate base costs
    first_question_cost = (SYSTEM_PROMPT_COST * CACHE_MULTIPLIER) + QUESTION_COST
    error_cost = (SYSTEM_PROMPT_COST * CACHE_MULTIPLIER) + (QUESTION_COST * CACHE_MULTIPLIER) + ERROR_COST
    format_cost = (
        (SYSTEM_PROMPT_COST * CACHE_MULTIPLIER) + (QUESTION_COST * CACHE_MULTIPLIER) + FORMAT_COST
        if caching
        else FORMAT_COST
    )

    # Total errors in all runs
    total_errors = runs * error_rate

    # Total costs
    total_cost = (
        runs * first_question_cost +
        total_errors * error_cost +
        runs * format_cost
    )

    return total_cost

def find_for_model(runs, initial_error_rate, step=1e-6, model="gpt-4o-mini"):
    error_rate = initial_error_rate
    while True:
        caching_cost = calculate_cost(True, runs, error_rate, model)
        no_caching_cost = calculate_cost(False, runs, error_rate, model)

        if caching_cost >= no_caching_cost:
            return error_rate, caching_cost, no_caching_cost

        error_rate -= step

def find_break_even_point(runs, initial_error_rate, models=None):
    """
    Finds and prints the break-even error rate for each model.

    Parameters:
        runs (int): Number of runs to simulate.
        initial_error_rate (float): Initial error rate to start the search from.
        models (list): List of model names to compare. If None, all models are compared.
    """
    # Collect results for each model
    results = []
    for model in models:
        error_rate, caching_cost, no_caching_cost = find_for_model(runs, initial_error_rate, model=model)
        results.append({
            "Model": model,
            "Break-even Error Rate (%)": error_rate * 100,
            "Caching Cost": caching_cost,
            "No Caching Cost": no_caching_cost,
            "Difference": abs(caching_cost - no_caching_cost)
        })

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    # Display results as a table
    print("\n", results_df, "\n")

def compare_costs_at_error_rates(runs, models, error_rates):
    """
    Compares caching and non-caching costs for predefined error rates for each model.

    Parameters:
        runs (int): Number of runs to simulate.
        error_rates (list): List of error rates for each model, in order.
        models (list): List of model names in the same order as error_rates.

    Returns:
        dict: A dictionary with models as keys and the cost comparison results as values.
    """
    

    results = {}
    for model, error_rate in zip(models, error_rates):
        caching_cost = calculate_cost(True, runs, error_rate, model=model)
        no_caching_cost = calculate_cost(False, runs, error_rate, model=model)
        
        results[model] = {
            "Error Rate (%)": error_rate * 100,
            "Caching Cost": round(caching_cost),
            "No Caching Cost": round(no_caching_cost),
            "Caching Cheaper": caching_cost < no_caching_cost,
            "Difference": round(abs(caching_cost - no_caching_cost)),
        }
    
    # Convert results to a DataFrame for easy visualization
    results_df = pd.DataFrame.from_dict(results, orient="index")
    print("\n", results_df, "\n")

if __name__ == "__main__":
    # Configuration
    runs = int(1e8)
    initial_error_rate = 0.33
    models = [
        "gpt-4o",
        "gpt-4o-mini",
        "o1-preview",
        "o1-mini"
    ]
    error_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

    # Functions
    find_break_even_point(runs, initial_error_rate, models)
    compare_costs_at_error_rates(runs, models, error_rates)