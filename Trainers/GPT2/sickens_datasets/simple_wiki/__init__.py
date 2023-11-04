from datasets import load_dataset
import torch

class Simple_Wiki:
	dataset_name="Simple_Wiki"

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
		title=data['title']
		text=data['text']

		data=self.tokenizer(f"{title} - {text}")

		data['labels']=data['input_ids']
		return data
