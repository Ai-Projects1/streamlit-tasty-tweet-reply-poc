import google.generativeai as genai
from rich import print

model = genai.GenerativeModel(model_name='models/gemini-1.5-flash-001')

query = '55'
result = model.generate_content(query)
print(f"Query: {query}, Result: {result.text}")

query = '123455'
result = model.generate_content(query)
print(f"Query: {query}, Result: {result.text}")

query = 'four'
result = model.generate_content(query)
print(f"Query: {query}, Result: {result.text}")

query = 'quatre'  # French 4
result = model.generate_content(query)
print(f"Query: {query}, Result: {result.text}")  # French 5 is "cinq"

query = 'III'  # Roman numeral 3
result = model.generate_content(query)
print(f"Query: {query}, Result: {result.text}")  # Roman numeral 4 is IV

query = '七'  # Japanese 7
result = model.generate_content(query)
print(f"Query: {query}, Result: {result.text}")  # Japanese 8 is 八!