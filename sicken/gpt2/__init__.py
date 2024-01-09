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

        self.chat_history_ids=None


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
        new_input_ids=self.gpt2_tokenizer.encode(question+ self.gpt2_tokenizer.eos_token, return_tensors='pt')
        bot_input_ids=torch.cat([self.chat_history_ids, new_input_ids], dim=-1) if self.chat_history_ids is not None else new_input_ids
        
        self.chat_history_ids=self.gpt2_model.generate(
            bot_input_ids,
            #pad_token_id=self.gpt2_tokenizer.eos_token,
            do_sample = True,
            top_k = 1,
            top_p = 0.20,
            max_length=1000,
            no_repeat_ngram_size=2, 
            temperature=0.76,
            early_stopping=True
            )

        return [self.gpt2_tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)]