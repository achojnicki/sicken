from datasets import load_dataset

class Sicken_Dataset:
	dataset_name="Sicken"

	def load_dataset(self):
		self.dataset=load_dataset(
			"json", 
			data_files={
				"train" : [
					"Datasets/Sicken/Data/Oxford_Dictionary.json"
					]
				} 
		)

	def process_function(self, data, rank):
		roles=data['word']
		contents=data['definition']

		model_inputs=self.tokenizer(roles)
		labels=self.tokenizer(text_target=contents)
		model_inputs["labels"]=labels['input_ids']
		return model_inputs

