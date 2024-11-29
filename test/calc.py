import pandas as pd
import json
import csv
import os

def get_total_results():
    # Define the folders
    folders = ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-4-turbo', 'gpt-3.5-turbo-0125']

    # Prepare the output file
    output_file = 'test/prelim_results.csv'

    # Define the header for the CSV file
    header = ['Model', 'Question', 'Input_size', 'Output_size', 'Time_taken', 'Attempts', 'Success', 'Tries', 'Accuracy_errors', 'Task_errors']

    # Open the output file for writing
    csvfile = open(output_file, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(header)

    # Iterate through each folder
    for folder in folders:
        model_name = folder  # Model name is the folder name
        results_path = os.path.join('test', folder, 'results.json')

        if not os.path.exists(results_path):
            print(f"Results file not found for {model_name}")
            continue

        jsonfile = open(results_path, 'r')
        data = json.load(jsonfile)

        # Iterate through each question in the results
        for question, details in data.items():
            question_number = int(question.replace('Question', ''))
            
            # Calculate the combined input and output token usage
            input_size = sum(
                details[item].get('InTokensUsed', 0)
                for item in details if isinstance(details[item], dict)
            )
            output_size = sum(
                details[item].get('OutTokensUsed', 0)
                for item in details if isinstance(details[item], dict)
            )

            # Calculate time taken (ResponseTimeSeconds)
            response_times = [
                details[item].get('ResponseTimeSeconds', 0)
                for item in details if isinstance(details[item], dict) and 'ResponseTimeSeconds' in details[item]
            ]
            time_taken = sum(response_times) if response_times else 0
            
            # Get the number of attempts and formatting/error entries
            tries = sum(
                1 for key in details if key.startswith(('Attempt', 'Formatting', 'Error'))
            )
            
            # Get success and attempts count
            attempts = details.get('Attempts', 0)
            success = details.get('Success', False)

            # Write the row to the CSV
            writer.writerow([model_name, question_number, input_size, output_size, time_taken, attempts, success, tries, 0, 0])
    csvfile.close()

    # Read the CSV files
    results_df = pd.read_csv('test/prelim_results.csv')
    costs_df = pd.read_csv('test/costs.csv')

    # Merge the two dataframes on the 'Model' column
    merged_df = pd.merge(results_df, costs_df, on='Model')

    # Calculate the total cost for each model
    merged_df['Cost'] = (merged_df['Input_size'] / 1000) * merged_df['In_cost_per_1k'] + (merged_df['Output_size'] / 1000) * merged_df['Out_cost_per_1k']

    # Drop unnecessary columns if needed (optional)
    merged_df = merged_df.drop(columns=['In_cost_per_1k', 'Out_cost_per_1k'])

    # Save the updated dataframe back to a CSV file
    merged_df.to_csv('test/total_results.csv', index=False)

    # Remove the preliminary results file
    os.remove('test/prelim_results.csv')

def get_final_info():
    print()
    models = ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-4-turbo', 'gpt-3.5-turbo-0125']

    # Read the CSV files
    results_df = pd.read_csv('test/total_results.csv')

    # Calculate the total cost for each model
    results = {}
    for model in models:
        # Cost is sum of 'Cost' column
        total_cost = results_df[results_df['Model'] == model]['Cost'].sum()
        # Accuracy = Success (True=1, False=0) * (1 / (1 + (Attempts - 1) + Accuracy_errors))

if __name__ == '__main__':
    get_total_results()
    #get_final_info()