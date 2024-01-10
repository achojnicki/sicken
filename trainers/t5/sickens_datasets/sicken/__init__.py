from datasets import load_dataset

class Sicken:
	dataset_name="sicken"
	dataset_type="sequence"

	def training_sequence(self):
		#inculcating categories
		self.load_categories()
		self.train(epochs=50)

		#inculcating Sicken's self
		self.load_self()
		self.train()

	def load_categories(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("categories.json")
					]
				} 
		)

	def load_self(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("sicken.json")
					]
				} 
		)



	def process_function(self, data):
		title=data['title']
		description=data['content']

		title=self.tokenizer(title)
		description=self.pagen(data)

		description=self.tokenizer(description)

		description['labels']=title['input_ids']
		return description

