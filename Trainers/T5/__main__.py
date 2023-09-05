from os import listdir
from multiprocess import set_start_method, freeze_support
from typing import List, Optional, Tuple
from transformers import AutoConfig, AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from platform import platform

import torch
import argparse
import Datasets


PROJECT_DIR="/Users/adrian/Dev/Sicken AI/" if 'macOS' in platform() else "/home/adrian/Dev/Sicken AI/"
MODELS_DIR=PROJECT_DIR+"Models/T5/"
DATASETS_DIR=PROJECT_DIR+"/Trainers/T5/Datasets"


class trainer_base:
	def __init__(self, args, model, tokenizer, collator):
		self.args=args

		self.model=model
		self.tokenizer=tokenizer
		self.data_collator=collator

		self.load_dataset()

	def train(self):
		self.train_dataset=self.dataset['train'].map(
			self.process_function,
			num_proc=int(self.args.workers_number),
			batched=True,
			with_rank=True,
			desc="Mapping Sicken on {dataset_name} dataset".format(dataset_name=self.dataset_name)
			)

		self.model_args=Seq2SeqTrainingArguments(
			output_dir=self.get_model_dir(),
			num_train_epochs=int(self.args.epochs),
			weight_decay=0.01,
			)

		self.trainer=Seq2SeqTrainer(
			model=self.model,
			args=self.model_args,
			train_dataset=self.train_dataset,
			tokenizer=self.tokenizer,
			data_collator=self.data_collator,
			)
		self.trainer.train()
		self.trainer.save_model(self._model_dir())

	def get_model_dir(self):
		return MODELS_DIR+self.args.model_name

class t5trainer:
	def __init__(self):
		arg=argparse.ArgumentParser(
			prog="Sicken T5 Trainer"
			)
		arg.add_argument(
			"model_name",
			help="Name of the model to be placed into the models directory"
			)
		arg.add_argument(
			"--epochs",
			default=1,
			help="Number of epochs"
			)
		arg.add_argument(
			"--workers_number",
			default=1,
			help="Number of workers"
			)
		arg.add_argument(
			"--model_template",
			default="Sicken_Base",
			help="Base model"
			)
		arg.add_argument(
			"--dataset",
			choices=self.list_all_datasets(),
			help="Datasets to use.",

			)

		self.args=arg.parse_args()

		self.device=torch.device("cuda" if torch.cuda.is_available() else 'cpu')
		self.load_model_tokenizer_collator()


	def load_model_tokenizer_collator(self):
		self.config = AutoConfig.from_pretrained(
		    self.get_base_model_dir(),
		    local_files_only=True
		)
		self.tokenizer = AutoTokenizer.from_pretrained(
		    self.get_base_model_dir(),
		    local_files_only=True
		)
		self.model = AutoModelForSeq2SeqLM.from_pretrained(
		    self.get_base_model_dir(),
		    config=self.config,
		    local_files_only=True
		)
		self.data_collator=DataCollatorForSeq2Seq(
			self.tokenizer
			)
		self.model.to(self.device)


	def get_base_model_dir(self):
		return MODELS_DIR+self.args.model_template

	def list_all_datasets(self):
			datasets=listdir(DATASETS_DIR)
			if ".DS_Store" in datasets:
			    datasets.remove(".DS_Store")
			if "__init__.py" in datasets:
				datasets.remove('__init__.py')
			if "__pycache__" in datasets:
				datasets.remove("__pycache__")

			return datasets

	def return_trainer_class(self, dataset_class):
		class trainer(trainer_base, dataset_class):
			pass
		return trainer

	def start(self):
		t=self.return_trainer_class(Datasets.datasets[self.args.dataset])
		t=t(self.args, self.model, self.tokenizer, self.data_collator)
		t.train()

if __name__=="__main__":
	freeze_support()
	set_start_method('spawn', force=True)

	app=t5trainer()
	app.start()




