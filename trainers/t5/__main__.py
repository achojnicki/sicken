#!/usr/bin/env python3
from os import listdir, environ
from multiprocess import set_start_method, freeze_support
from transformers import T5Config, AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from argparse import ArgumentParser

from constants import T5_Trainer_Constants
from pagen import Pagen

import sickens_datasets


class trainer_base:
	def __init__(self, constants,  args, model, tokenizer, collator):
		self.constants=constants
		self.args=args

		self.model=model
		self.tokenizer=tokenizer
		self.data_collator=collator

		self.pagen=Pagen()

	def return_dataset_file_path(self, file):
		return str(self.constants.datasets_dir / self.dataset_name / file)

	def train(self, epochs=None):
		self.train_dataset=self.train_dataset.map(
			self.process_function,
			num_proc=self.args.num_workers,
			desc=f"Mapping Sicken on the {self.dataset_name} dataset"
			)

		self.model_args=Seq2SeqTrainingArguments(
			output_dir=self.get_model_dir(),
			seed=76,
			overwrite_output_dir=True,
			weight_decay=self.args.weight_decay,
			num_train_epochs=epochs if epochs else self.args.epochs,
			per_device_train_batch_size=self.args.batch_size,
			no_cuda=True if not self.args.use_cuda else False,
			use_cpu=True if not self.args.use_cuda and self.args.use_cpu else False,
			use_ipex=self.args.use_ipex,
			fp16=True if self.args.use_fp16 else False,
			save_strategy="no",
			)

		self.trainer=Seq2SeqTrainer(
			model=self.model,
			args=self.model_args,
			train_dataset=self.train_dataset,
			tokenizer=self.tokenizer,
			data_collator=self.data_collator,
			)

		self.trainer.train()

	def save_model(self):
		self.trainer.save_model(self.get_model_dir())

	def get_model_dir(self):
		return self.constants.models_dir / self.args.new_model_name

class T5_Trainer:
	def __init__(self):
		self.constants=T5_Trainer_Constants
		self.args=self.parse_args()

		if self.args.use_cuda:
			environ['PYTORCH_CUDA_ALLOC_CONF']='garbage_collection_threshold:0.6,max_split_size_mb:32'
			freeze_support()
			set_start_method('spawn', force=True)

		self.load_model_tokenizer_collator()

	def parse_args(self):
		arg=ArgumentParser(
				prog="sickenstrainer_t5"
				)

		arg.add_argument(
			"--new_model_name",
			required=True,
			help="name of the new model"
			)

		gr1=arg.add_mutually_exclusive_group(required=True)

		gr1.add_argument(
			"--base_model",
			choices=self.list_all_models(),
			help="base model"
			)

		gr1.add_argument(
			"--base_config",
			choices=self.list_all_configs(),
			help="base config"
			)

		arg.add_argument(
			"--tokenizer",
			required=True,
			choices=self.list_all_tokenizers(),
			help="tokenizer"
			)

		arg.add_argument(
			"--dataset",
			required=True,
			choices=self.list_all_datasets(),
			help="dataset to use",
			)

		arg.add_argument(
			"--num_workers",
			default=1,
			type=int,
			help="number of workers processes"
			)

		arg.add_argument(
			"--epochs",
			default=1,
			type=int,
			help="number of epochs"
			)

		arg.add_argument(
			"--batch_size",
			default=1,
			type=int,
			help="size of the batch")

		arg.add_argument(
			"--weight_decay",
			default=0.01,
			type=float,
			help="weight decay")

		gr2=arg.add_mutually_exclusive_group(required=True)

		gr2.add_argument(
			'--use_cpu',
			action='store_true',
			help='use CPU to train'
			)

		gr2.add_argument(
			'--use_cuda',
			action='store_true',
			help='use CUDA to train'
			)

		gr2.add_argument(
			'--use_mps',
			action='store_true',
			help='Use MPS device to train')

		arg.add_argument(
			'--use_ipex',
			action='store_true',
			help='use IPEX'
			)

		arg.add_argument(
			'--use_fp16',
			action='store_true',
			help='use BFLOAT16'
			)

		return arg.parse_args()

	def load_model_tokenizer_collator(self):
		if self.args.base_model:
			self.config = T5Config.from_pretrained(
			    self.get_base_model_path(),
			    local_files_only=True
			)
			self.model = AutoModelForSeq2SeqLM.from_pretrained(
			    self.get_base_model_path(),
			    config=self.config,
			    local_files_only=True
			)

		elif self.args.base_config:
			self.config=T5Config.from_json_file(
				self.get_base_config_path(),
				)

			self.model=AutoModelForSeq2SeqLM.from_config(
				self.config,
				)	

		self.tokenizer = AutoTokenizer.from_pretrained(
		    self.get_tokenizer_path(),
		    local_files_only=True
			)

		self.data_collator=DataCollatorForSeq2Seq(
			tokenizer=self.tokenizer,
			model=self.model
			)

	def get_base_model_path(self):
		return self.constants.models_dir / self.args.base_model
	
	def get_base_config_path(self):
		return self.constants.configs_dir / self.args.base_config / 'config.json'

	def get_tokenizer_path(self):
		return self.constants.tokenizers_dir / self.args.tokenizer

	def list_all_datasets(self):
		datasets=listdir(self.constants.datasets_dir)
		if ".DS_Store" in datasets:
		    datasets.remove(".DS_Store")
		if "__init__.py" in datasets:
			datasets.remove('__init__.py')
		if "__pycache__" in datasets:
			datasets.remove("__pycache__")

		return datasets

	def list_all_configs(self):
		configs=listdir(self.constants.configs_dir)
		if ".DS_Store" in configs:
		    configs.remove(".DS_Store")

		return configs

	def list_all_models(self):
	    models=listdir(self.constants.models_dir)
	    if ".DS_Store" in models:
	        models.remove(".DS_Store")
	    return models

	def list_all_tokenizers(self):
	    tokenizers=listdir(self.constants.tokenizers_dir)
	    if ".DS_Store" in tokenizers:
	        tokenizers.remove(".DS_Store")
	    return tokenizers

	def return_trainer_class(self, dataset_class):
		class trainer(trainer_base, dataset_class):
			pass
		return trainer

	def start(self):
		t=self.return_trainer_class(sickens_datasets.all_datasets[self.args.dataset])
		t=t(
			self.constants,
			self.args,
			self.model,
			self.tokenizer,
			self.data_collator
			)

		if t.dataset_type == "simple":
			t.load_dataset()
			t.train()

		elif t.dataset_type =='sequence':
			t.training_sequence()

		t.save_model()

if __name__=="__main__":
	app=T5_Trainer()
	app.start()
