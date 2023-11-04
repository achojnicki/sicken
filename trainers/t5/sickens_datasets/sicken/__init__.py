from datasets import load_dataset

class Sicken:
	dataset_name="Sicken"

	def load_dataset(self):
		self.train_dataset=load_dataset(
			"json",
			split='train',
			data_files={
				"train" : [
					self.return_dataset_file_path("Sicken.json"),
					self.return_dataset_file_path("Relations.json"),
					self.return_dataset_file_path("Adrian_Chojnicki.json"),
					self.return_dataset_file_path("Preferences.json"),
					self.return_dataset_file_path("ESP_knowledge.json"),
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

