from datasets import load_dataset

class Sicken:
	dataset_name="sicken"

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
		role=data['role']
		content=data['content']

		data=self.tokenizer(f"{role} - {content}")

		data['labels']=data['input_ids']
		return data

