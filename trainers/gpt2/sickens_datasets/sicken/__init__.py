from datasets import load_dataset

class Sicken:
	dataset_name="sicken"
	dataset_type="sequence"

	def training_sequence(self):
		#inculcating Oxford Dictionary
		self.load_dictionary()
		self.train(epochs=1, map_function=self.map_dictionary)

		#inculcating Wikipedia articles
		self.load_wiki()
		self.train(epochs=1, map_function=self.map_wiki)

		#inculcating categories
		self.load_categories()
		self.train(epochs=7)

		#inculcating Sicken's self
		self.load_self()
		self.train(epochs=7)

		#inculcating rules
		self.load_rules()
		self.train(epochs=7)

		#finetune
		self.load_finetune()
		self.train(epochs=7, map_function=self.map_finetune)


	def load_wiki(self):
		self.train_dataset=load_dataset(
			"json",
			split='train', 
			data_files={
				"train" : [
					self.return_dataset_file_path("wiki_en.json")
					]
				} 
		)

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
		example=f"{data['word']} - {data['definition']}"
		example=self.tokenizer(example)

		example['labels']=example['input_ids']
		return example


	def map_finetune(self, data):
		example=f"{data['reply_type']}\n\n{data['reply']}"
		example=self.tokenizer(example)

		example['labels']=example['input_ids']
		return example

	def map_pagen(self, data):
		example=self.pagen(data)
		example=self.tokenizer(example)

		example['labels']=example['input_ids']
		return example

	def map_wiki(self, data):
		example=data['content']
		example=self.tokenizer(example)

		example['labels']=example['input_ids']
		return example


