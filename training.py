import google.generativeai as genai
import time
import json
base_model = "models/gemini-1.5-pro-002-tuning"

with open(f'assets/training_data.json', 'r') as file:
    training_data = json.load(file)

print('training_data',training_data)
operation = genai.create_tuned_model(
    # You can use a tuned model here too. Set `source_model="tunedModels/..."`
    display_name="trained_images",
    source_model=base_model,
    epoch_count=20,
    batch_size=4,   
    learning_rate=0.001,
    training_data=training_data,
)

for status in operation.wait_bar():
    time.sleep(10)

result = operation.result()
print(result)
# # You can plot the loss curve with:
# snapshots = pd.DataFrame(result.tuning_task.snapshots)
# sns.lineplot(data=snapshots, x='epoch', y='mean_loss')