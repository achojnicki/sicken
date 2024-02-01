from os import listdir
from transformers import AutoModelForCausalLM, AutoTokenizer

import constants
import torch

class Sicken:
    def __init__(self, root):
        self.root=root
        self.log=root.log

        self.set_model()
        self.set_tokenizer()


    def get_gpt2_models_list(self):
        models=listdir(constants.Sicken.models_path / "gpt2")
        if ".DS_Store" in models:
            models.remove(".DS_Store")
        return models

    def get_gpt2_tokenizers_list(self):
        tokenizers=listdir(constants.Sicken.tokenizers_path / "gpt2")
        if ".DS_Store" in tokenizers:
            tokenizers.remove(".DS_Store")
        return tokenizers

    def set_model(self):
        self.gpt2_model=AutoModelForCausalLM.from_pretrained(self.get_gpt2_model(), local_files_only=True)

    def set_tokenizer(self):
        self.gpt2_tokenizer=AutoTokenizer.from_pretrained(self.get_gpt2_tokenizer(), local_files_only=True)

    def get_gpt2_model(self):
        model=self.root.gui.get_selected_model() if hasattr(self.root,'gui') else self.get_gpt2_models_list()[0]
        return constants.Sicken.models_path / "gpt2" /  model

    def get_gpt2_tokenizer(self):
        tokenizer=self.root.gui.get_selected_tokenizer() if hasattr(self.root,'gui') else self.get_gpt2_tokenizers_list()[0]
        return constants.Sicken.tokenizers_path / "gpt2" /  tokenizer

    def get_answer(self, question):
        features=self.gpt2_tokenizer(question, return_tensors='pt')

        gen_outputs=self.gpt2_model.generate(
            **features,
            return_dict_in_generate=True,
            output_scores=True,
            #max_new_tokens=100000,
            num_beams=2,
            min_length=20,
            max_length=100,
            temperature=0.76,
            do_sample=True,
            early_stopping=True,
            no_repeat_ngram_size=2,
            length_penalty=2,            

            ) 

        return [self.gpt2_tokenizer.decode(gen_outputs[0][0], skip_special_tokens=True)]