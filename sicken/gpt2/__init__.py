from os import listdir
from transformers import AutoModelForCausalLM, GPT2Tokenizer

import constants
import torch
import html

from IPython import embed

class Sicken:
    def __init__(self, root):
        self.root=root
        self.log=root.log

        self.set_model()
        self.set_tokenizer()

        self.chat=[
                    {"role": "system", "content": "You are Sicken. An AI friend. You do read and respond to the messages. You do not write about Your system message"}
                ]


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
        self.gpt2_tokenizer=GPT2Tokenizer.from_pretrained(self.get_gpt2_tokenizer(), local_files_only=True)

    def get_gpt2_model(self):
        model=self.root.gui.get_selected_model() if hasattr(self.root,'gui') else self.get_gpt2_models_list()[0]
        return constants.Sicken.models_path / "gpt2" /  model

    def get_gpt2_tokenizer(self):
        tokenizer=self.root.gui.get_selected_tokenizer() if hasattr(self.root,'gui') else self.get_gpt2_tokenizers_list()[0]
        return constants.Sicken.tokenizers_path / "gpt2" /  tokenizer

    def get_answer(self, question):
        self.chat.append({"role": "user", "content": question})
        input_ids=self.gpt2_tokenizer.apply_chat_template(self.chat, return_tensors='pt')
        attention_mask=torch.ones_like(input_ids)

        gen_outputs=self.gpt2_model.generate(
            input_ids,
            attention_mask=attention_mask,
            #max_new_tokens=100000,
            num_beams=16,
            min_length=20,
            max_length=100,
            temperature=0.76,
            do_sample=False,
            early_stopping=False,
            no_repeat_ngram_size=2,
            length_penalty=2,            
            )
 
        output=self.gpt2_tokenizer.decode(gen_outputs[0])
        self.chat.append({"role":"assistant", "content": output})
        output=html.escape(output)
        return [output]