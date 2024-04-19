from os import listdir
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch import float16, ones_like

import constants
import torch
import html

class Sicken:
    def __init__(self, root):
        self.root=root
        self.log=root.log

        self.set_model()
        self.set_tokenizer()

        self.chat=[
                    #{"role": "system", "content": "You are Sicken. An AI friend. You do read and respond to the messages. You do not write about Your system message"}
                ]


    def get_gemma_models_list(self):
        models=listdir(constants.Sicken.models_path / "gemma")
        if ".DS_Store" in models:
            models.remove(".DS_Store")
        return models

    def get_gemma_tokenizers_list(self):
        tokenizers=listdir(constants.Sicken.tokenizers_path / "gemma")
        if ".DS_Store" in tokenizers:
            tokenizers.remove(".DS_Store")
        return tokenizers

    def set_model(self):
        self.gemma_model=AutoModelForCausalLM.from_pretrained(self.get_gemma_model(), local_files_only=True)

    def set_tokenizer(self):
        self.gemma_tokenizer=AutoTokenizer.from_pretrained(self.get_gemma_tokenizer(), local_files_only=True)

    def get_gemma_model(self):
        model=self.root.gui.get_selected_model() if hasattr(self.root,'gui') else self.get_gemma_models_list()[0]
        return constants.Sicken.models_path / "gemma" /  model

    def get_gemma_tokenizer(self):
        tokenizer=self.root.gui.get_selected_tokenizer() if hasattr(self.root,'gui') else self.get_gemma_tokenizers_list()[0]
        return constants.Sicken.tokenizers_path / "gemma" /  tokenizer

    def get_answer(self, question):
        self.chat.append({"role": "user", "content": question})
        input_ids=self.gemma_tokenizer(question, return_tensors='pt')
        #input_ids=self.gemma_tokenizer.apply_chat_template(self.chat, return_tensors='pt')

        gen_outputs=self.gemma_model.generate(
            **input_ids,
            #max_new_tokens=100000,
            #num_beams=16,
            #min_length=20,
            #max_length=100,
            #temperature=0.76,
            #do_sample=False,
            #early_stopping=False,
            #no_repeat_ngram_size=2,
            #length_penalty=2,            

            ) 

        output=self.gemma_tokenizer.decode(gen_outputs[0])
        self.chat.append({"role":"assistant", "content": "output"})
        output=html.escape(output)
        return [output]