from datasets import load_dataset

class Oxford_Dictionary:
	dataset_name="oxford_dictionary"

	def load_dataset(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("Oxford_Dictionary.json")
					]
				} 
		)

	def process_function(self, data):
		roles=data['word']
		contents=data['definition']

		model_inputs=self.tokenizer(roles)
		labels=self.tokenizer(text_target=contents)
		model_inputs["labels"]=labels['input_ids']
		return model_inputs

