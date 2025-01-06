import pandas as pd
import json
import os

def get_total_results():
    folders = ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-4-turbo', 'gpt-3.5-turbo-0125']
    output_file = 'test/results.csv'
    
    # Initialize an empty DataFrame
    columns = ['Model', 'Question', 'Input_size', 'Output_size', 'Time_taken', 'Attempts', 
               'Success', 'Tries', 'Accuracy_errors', 'Task_errors']
    results_df = pd.DataFrame(columns=columns)

    # Iterate through each folder
    for folder in folders:
        model_name = folder
        results_path = os.path.join('test', folder, 'results.json')

        if not os.path.exists(results_path):
            print(f"Results file not found for {model_name}")
            continue

        with open(results_path, 'r') as jsonfile:
            data = json.load(jsonfile)

        # Process each question in the results
        for question, details in data.items():
            question_number = int(question.replace('Question', ''))
            
            # Calculate input and output token usage
            input_size = sum(
                details[item].get('InTokensUsed', 0)
                for item in details if isinstance(details[item], dict)
            )
            output_size = sum(
                details[item].get('OutTokensUsed', 0)
                for item in details if isinstance(details[item], dict)
            )
            
            # Calculate time taken
            response_times = [
                details[item].get('ResponseTimeSeconds', 0)
                for item in details if isinstance(details[item], dict) and 'ResponseTimeSeconds' in details[item]
            ]
            time_taken = sum(response_times) if response_times else 0

            # Count tries, task_errors, and accuracy_errors
            tries = sum(1 for key in details if key.startswith(('Attempt', 'Formatting', 'Accuracy_Error', 'Task_Error')))
            task_errors = sum(1 for key in details if key.startswith('Task_Error'))
            acc_errors = sum(1 for key in details if key.startswith('Accuracy_Error'))

            # Get attempts and success status
            attempts = details.get('Attempts', 0)
            success = details.get('Success', False)

            # Append a row to the DataFrame
            results_df = results_df._append({
                'Model': model_name,
                'Question': question_number,
                'Input_size': input_size,
                'Output_size': output_size,
                'Time_taken': time_taken,
                'Attempts': attempts,
                'Success': success,
                'Tries': tries,
                'Accuracy_errors': acc_errors,
                'Task_errors': task_errors
            }, ignore_index=True)

    # Save the DataFrame to a CSV file
    results_df.to_csv(output_file, index=False)

def get_final_info():
    print()
    models = ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-4-turbo', 'gpt-3.5-turbo-0125']

    # Read the CSV files
    results_df = pd.read_csv('test/results.csv')
    costs_df = pd.read_csv('test/costs.csv')

    # Calculate the total cost for each model
    results = {model: {} for model in models}
    for model in models:
        model_df = results_df[results_df['Model'] == model]
        
        # Cost is sum of 'Cost' column
        total_in = model_df['Input_size'].sum()
        total_out = model_df['Output_size'].sum()
        thou_in = costs_df[costs_df['Model'] == model]['In_cost_per_1k'].sum()
        thou_out = costs_df[costs_df['Model'] == model]['Out_cost_per_1k'].sum()
        results[model]['Cost'] = round(float(((total_in / 1000) * thou_in) + ((total_out / 1000) * thou_out)), 2)
        
        # Accuracy = Success (True=1, False=0) * (1 / (1 + (Attempts - 1) + Accuracy_errors))
        total_accuracy = 0
        for index, row in model_df.iterrows():
            success = 1 if row['Success'] == True else 0
            total_accuracy += success * (1 / (1 + (row['Attempts'] - 1) + row['Accuracy_errors']))
        results[model]['Accuracy'] = round(total_accuracy, 2)
        
        # Taskability = 1 / (1 + Task_errors) 
        total_task = 0
        for index, row in model_df.iterrows():
            total_task += 1 / (1 + row['Task_errors'])
        results[model]['Taskability'] = round(total_task, 2)
        
        # Speed = (sum(In_tokens) + sum(Out_tokens)) / sum(Response_time) -> processed tokens per second 
        total_speed = (sum(model_df['Input_size']) + sum(model_df['Output_size'])) / sum(model_df['Time_taken'])
        results[model]['Speed'] = round(total_speed, 2)
    return results

def calculate_scores(models_dict):
    # Extract values for Cost and Speed
    cost_values = [v['Cost'] for v in models_dict.values()]
    speed_values = [v['Speed'] for v in models_dict.values()]

    # Get the worst and best values for each variable
    worst_best = {
        'Cost': (max(cost_values), min(cost_values)),
        'Accuracy': (0, 9),
        'Taskability': (0, 9),
        'Speed': (min(speed_values), max(speed_values)),
    }
    
    weights = {
        'Cost': 4,
        'Accuracy': 3,
        'Taskability': 2,
        'Speed': 1
    }

    # Normalize and calculate scores
    normalized_dict = {}
    weighted_dict = {}
    for model, stats in models_dict.items():
        normalized = {
            'Cost': 100 * (worst_best['Cost'][0] - stats['Cost']) / (worst_best['Cost'][0] - worst_best['Cost'][1]),
            'Accuracy': 100 * (stats['Accuracy'] - worst_best['Accuracy'][0]) / (worst_best['Accuracy'][1] - worst_best['Accuracy'][0]),
            'Taskability': 100 * (stats['Taskability'] - worst_best['Taskability'][0]) / (worst_best['Taskability'][1] - worst_best['Taskability'][0]),
            'Speed': 100 * (stats['Speed'] - worst_best['Speed'][0]) / (worst_best['Speed'][1] - worst_best['Speed'][0])
        }
        # Store normalized values
        normalized_dict[model] = normalized
        
        weighted = {key: round(value * weights[key], 2) for key, value in normalized.items()}
        weighted['Score'] = round(sum(weighted.values()), 2)
        weighted_dict[model] = weighted
    
    return normalized_dict, weighted_dict
    
if __name__ == '__main__':
    # get_total_results()
    
    results = get_final_info()
    
    normalized_dict, weighted_dict = calculate_scores(results)
    for key in weighted_dict.keys():
        print(key, weighted_dict[key])