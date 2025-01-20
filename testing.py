import google.generativeai as genai
import random
import time
from rich import print

# List tuned models
# for i, m in zip(range(5), genai.list_tuned_models()):
#     print(m.name)

# Evaluate the model
model = genai.GenerativeModel(model_name='tunedModels/increment-ge4tnp7qw5cc')
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

query = '55'
result = model.generate_content(query,safety_settings=safety_settings,stream=True)
for chunk in result:
    print(chunk.text)
    print("_" * 80)

# # query = '123455'
# # result = model.generate_content(query)
# # print(f"Query: {query}, Result: {result.text}")

# # query = 'four'
# # result = model.generate_content(query)
# # print(f"Query: {query}, Result: {result.text}")

# # query = 'quatre'  # French 4
# # result = model.generate_content(query)
# # print(f"Query: {query}, Result: {result.text}")  # French 5 is "cinq"

# # query = 'III'  # Roman numeral 3
# # result = model.generate_content(query)
# # print(f"Query: {query}, Result: {result.text}")  # Roman numeral 4 is IV

# # query = '七'  # Japanese 7
# # result = model.generate_content(query)
# # print(f"Query: {query}, Result: {result.text}")  # Japanese 8 is 八!

# # # Update model description
# # name = 'generate-num-mervinpraison-9'
# # genai.update_tuned_model(f'tunedModels/{name}', {"description": "This is Mervin Praison model."})
# # model = genai.get_tuned_model(f'tunedModels/{name}')
# print(f"Model: {name}, Description: {model.description}")