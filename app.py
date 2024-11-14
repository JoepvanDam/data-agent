import os
import ast
import ollama
import pandas as pd

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

    # Make a prompt
    prompt = f"""
    Data file name: {file_name}
    Number of rows: {data.shape[0]}
    Column info: {column_info}

    ---
    Based on the user question, return which function(s) should be used on which columns in order to answer the question. Please return the exact code necessary to answer the question.
    
    Rules:
    - ONLY return code. No additional information should be provided. Your response should be the exact code that needs to be executed. This means you should never include ```, comments, or any other information that is not code.
    - Allowed libraries include: pandas, numpy, matplotlib, seaborn, scikit-learn, scipy, and standard python libraries.
    - Explicitly disallowed libraries include: os, sys, subprocess, and any other library that can be used to execute code.

    ---
    User Question:
    {user_question}
    """

    # Get response from the model
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )
    response_content = response['message']['content']
    print('\n', response_content, '\n')
    
    # Parse the response
    file_path = 'generated_script.py'
    with open(file_path, 'w') as file:
        file.write(response_content)

    # Execute the script
    with open(file_path, 'r') as file:
        code = file.read()
        if is_safe_code(code):
            exec(code)
        else:
            print('Unsafe code detected. Exiting...')

    # Clean up
    os.remove(file_path)

def is_safe_code(code):
    # Parse the code into an Abstract Syntax Tree (AST)
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False  # If the code is invalid, consider it unsafe

    # Check for disallowed nodes in the AST
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Call)):
            # Check for unsafe function calls (like exec or eval)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {'exec', 'eval', 'open', 'subprocess', 'os', 'sys'}:
                    return False
            # Check for imports of disallowed modules
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name in {'os', 'sys', 'subprocess'}:
                        return False
    return True


if __name__ == '__main__':
    main()
