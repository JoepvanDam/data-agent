import os
import json
import csv

# Define the folders
folders = ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-4-turbo', 'gpt-3.5-turbo-0125']

# Prepare the output file
output_file = 'test/results.csv'

# Define the header for the CSV file
header = ['Model', 'Question', 'Input_size', 'Output_size', 'Attempts', 'Success', 'Tries']

# Open the output file for writing
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)

    # Iterate through each folder
    for folder in folders:
        model_name = folder  # Model name is the folder name
        results_path = os.path.join('test', folder, 'results.json')

        if os.path.exists(results_path):
            with open(results_path, 'r') as jsonfile:
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
                    
                    # Get the number of attempts and formatting/error entries
                    tries = sum(
                        1 for key in details if key.startswith(('Attempt', 'Formatting', 'Error'))
                    )
                    
                    # Get success and attempts count
                    attempts = details.get('Attempts', 0)
                    success = details.get('Success', False)

                    # Write the row to the CSV
                    writer.writerow([model_name, question_number, input_size, output_size, attempts, success, tries])

print(f"Results written to {output_file}")