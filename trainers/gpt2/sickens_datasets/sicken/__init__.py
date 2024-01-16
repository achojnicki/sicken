from datasets import load_dataset

class Sicken:
	dataset_name="sicken"
	dataset_type="sequence"

	def training_sequence(self):
		#inculcating categories
		self.load_categories()
		self.train(epochs=100)

		#inculcating Sicken's self
		self.load_self()
		self.train()

		#inculcating rules
		self.load_rules()
		self.train(epochs=100)

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

	def load_rules(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("rules.json")
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
		description=data['content']

		description=self.pagen(data)
		description=self.tokenizer(description)

		description['labels']=description['input_ids']
		return description


