from datasets import load_dataset

import numpy

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


	def compute_metrics(self, data):
		print(data)
		logits, labels = data
		predictions = numpy.argmax(logits, axis=-1)
		return self.metric_acc.compute(predictions=predictions, references=labels)

	def process_function(self, data):
		title=data['title']
		description=data['content']

		title=self.tokenizer(title)
		description=self.pagen(data)

		description=self.tokenizer(description)

		description['labels']=title['input_ids']
		return description

