from datasets import load_dataset
import torch

class Simple_Wiki:
	dataset_name="simple_wiki"

	def load_dataset(self):
		self.train_dataset=load_dataset(
			"json",
			split='train',
			data_files={
				"train" : [
					self.return_dataset_file_path("Simple_Wiki.json")
					]
				} 
		)

	def process_function(self, data):
		roles=data['title']
		contents=data['text']

		model_inputs=self.tokenizer(roles)
		labels=self.tokenizer(text_target=contents)
		model_inputs["labels"]=labels['input_ids']
		return model_inputs

