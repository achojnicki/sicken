from datasets import load_dataset

class Oxford_Dictionary:
	dataset_name="Oxford_Dictionary"

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
		word=data['word']
		definition=data['definition']

		data=self.tokenizer(f"{word} - {definition}")

		data['labels']=data['input_ids']
		return data

