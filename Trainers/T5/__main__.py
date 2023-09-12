#!/usr/bin/env python3
from os import listdir, environ
from multiprocess import set_start_method, freeze_support
from transformers import AutoConfig, AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from argparse import ArgumentParser

from Constants import T5_Trainer_Constants

import Datasets


class trainer_base:
	def __init__(self, constants,  args, model, tokenizer, collator):
		self.constants=constants
		self.args=args

		self.model=model
		self.tokenizer=tokenizer
		self.data_collator=collator

		self.load_dataset()



	def return_dataset_file_path(self, file):
		return str(self.constants.datasets_dir / self.dataset_name / "Data" / file)

	def train(self):
		self.train_dataset=self.train_dataset.map(
			self.process_function,
			num_proc=self.args.num_workers,
			desc="Mapping Sicken on the {dataset} dataset".format(dataset=self.dataset_name)
			)

		self.model_args=Seq2SeqTrainingArguments(
			output_dir=self.get_model_dir(),
			seed=76,
			overwrite_output_dir=True,
			weight_decay=self.args.weight_decay,
			num_train_epochs=self.args.epochs,
			per_device_train_batch_size=self.args.batch_size,
			no_cuda=not self.args.use_cuda,
			use_cpu=self.args.use_cpu,
			use_ipex=self.args.use_ipex,
			fp16=True if self.args.use_cuda else False,
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
		self.trainer.save_model(self.get_model_dir())

	def get_model_dir(self):
		return self.constants.models_dir / self.args.model_name

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
				prog="sicken_t5_trainer"
				)

		arg.add_argument(
			"--model_name",
			required=True,
			help="name of the new model"
			)

		arg.add_argument(
			"--model_base",
			required=True,
			choices=self.list_all_models(),
			help="base model"
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

		gr=arg.add_mutually_exclusive_group()

		gr.add_argument(
			'--use_cpu',
			action='store_true',
			help='use CPU to train'
			)

		gr.add_argument(
			'--use_cuda',
			action='store_true',
			help='use CUDA to train'
			)

		arg.add_argument(
			'--use_ipex',
			action='store_true',
			help='use IPEX'
			)
		return arg.parse_args()

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

	def get_base_model_dir(self):
		return self.constants.models_dir / self.args.model_base

	def list_all_datasets(self):
		datasets=listdir(self.constants.datasets_dir)
		if ".DS_Store" in datasets:
		    datasets.remove(".DS_Store")
		if "__init__.py" in datasets:
			datasets.remove('__init__.py')
		if "__pycache__" in datasets:
			datasets.remove("__pycache__")

		return datasets

	def list_all_models(self):
	    models=listdir(self.constants.models_dir)
	    if ".DS_Store" in models:
	        models.remove(".DS_Store")
	    return models

	def return_trainer_class(self, dataset_class):
		class trainer(trainer_base, dataset_class):
			pass
		return trainer

	def start(self):
		t=self.return_trainer_class(Datasets.datasets[self.args.dataset])
		t=t(self.constants, self.args, self.model, self.tokenizer, self.data_collator)
		t.train()

if __name__=="__main__":
	app=T5_Trainer()
	app.start()




