from gpt4all import GPT4All

model = GPT4All("path/to/gpt4all-lora-quantized.bin")
prompt = "Give me a 400 kcal vegetarian lunch idea."
response = model.generate(prompt)
print(response)
