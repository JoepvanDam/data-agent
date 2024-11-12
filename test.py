##### NEVER EVER (!!!!!) put any sensitive data in here. 
##### A connection is made to an API. Maybe it's safe, maybe it's not.
##### BUT - DO NOT RISK IT!
##### If you want to start using sensitive data, download a model and use it locally.

from transformers import LlamaForCausalLM, LlamaTokenizer, pipeline

model_name = "meta-llama/Llama-3.2-1B"
model = LlamaForCausalLM.from_pretrained(model_name)
tokenizer = LlamaTokenizer.from_pretrained(model_name)

# Create a text generation pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Generate a response
response = pipe("Hey, how are you doing today?")
print(response[0]['generated_text'])
