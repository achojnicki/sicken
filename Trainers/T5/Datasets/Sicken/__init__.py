from datasets import load_dataset

class Sicken_Dataset:
	dataset_name="Sicken"

	def load_dataset(self):
		self.train_dataset=load_dataset(
			"json",
			split='train',
			data_files={
				"train" : [
					"Datasets/Sicken/Data/Sicken.json",
					"Datasets/Sicken/Data/Relations.json",
					"Datasets/Sicken/Data/Adrian_Chojnicki.json",
					"Datasets/Sicken/Data/Preferences.json",
					"Datasets/Sicken/Data/ESP_knowledge.json",
					]
				} 
		)

	def process_function(self, data):
		roles=data['role']
		contents=data['content']

		model_inputs=self.tokenizer(roles)
		labels=self.tokenizer(text_target=contents)
		model_inputs["labels"]=labels['input_ids']
		return model_inputs

