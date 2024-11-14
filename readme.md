# Ollama Installation Guide
This guide covers the installation of both the Ollama CLI and the Python library.

## Prerequisites
- **macOS, Windows, or Linux** for the Ollama CLI.
- **Python 3.7 or higher** (if using the Python library).

---

## Step 1: Install the Ollama CLI
### macOS & Windows
1. Go to the [Ollama website](https://ollama.com/download).
2. Download the installer for your platform and follow the on-screen instructions.

### Linux
Open a terminal and run the following command to install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Once installed, verify the installation by checking the version:

```bash
ollama --version
```

## Step 2: Download the Llama model
After installing Ollama, you can download a model to run locally. For example, to download the Llama 3.2 model, use:
```bash
ollama pull llama3.2
```

## Step 3: Run the Llama model
Once the model is downloaded, start the model by running:

```bash
ollama run llama3.2
```
This command will launch the Llama 3.2 model, allowing you to enter prompts and receive responses directly in the terminal.

## Step 4: Install the Python library
If you'd like to use Ollama programatically, install the Python library:
```bash
pip install ollama
```

Verify the installation
```bash
python -m pip show ollama
```

### Example usage
With the library installed, you can interact with the model in Python:
```py
import ollama

response = ollama.chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': 'What is the capital of France?'}]
)

print(response['message']['content'])
```