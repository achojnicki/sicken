from datasets import load_dataset

class Sicken:
	dataset_name="sicken"
	dataset_type="sequence"

	def training_sequence(self):
		#inculcating Oxford Dictionary
		self.load_dictionary()
		self.train(epochs=1, map_function=self.map_dictionary)

		#inculcating categories
		self.load_categories()
		self.train(epochs=100)

		#inculcating Sicken's self
		self.load_self()
		self.train()

		#inculcating rules
		self.load_rules()
		self.train(epochs=100)

		#finetune
		self.load_finetune()
		self.train(epochs=1000, map_function=self.map_finetune)


	def load_dictionary(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("oxford_dictionary.json")
					]
				} 
		)

	def load_finetune(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("finetune.json")
					]
				} 
		)

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


	def map_dictionary(self, data):
		description=f"{data['word']} - {data['definition']}"
		description=self.tokenizer(description)

		description['labels']=description['input_ids']
		return description


	def map_finetune(self, data):
		description=f"{data['reply_type']}\n\n{data['reply']}"
		description=self.tokenizer(description)

		description['labels']=description['input_ids']
		return description

	def map_pagen(self, data):
		description=self.pagen(data)
		data=self.tokenizer(description)

		data['labels']=data['input_ids']
		return data


