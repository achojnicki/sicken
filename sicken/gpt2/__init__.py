from sicken import constants

from os import listdir
from transformers import GPT2LMHeadModel, GPT2Tokenizer

import html

DEFAULT_PARAMETERS={
    "return_dict_in_generate":True,
    "output_scores":True,
    #"max_new_tokens":100000,
    "num_beams":2,
    "min_length":20,
    "max_length":100,
    "temperature":0.76,
    "do_sample":True,
    "early_stopping":True,
    "no_repeat_ngram_size":2,
    "length_penalty":2 
}


class Sicken:
    def __init__(self, root, model, tokenizer):
        self._root=root
        self._log=root._log

        self._set_model(self._get_gpt2_model_path(model))
        self._set_tokenizer(self._get_gpt2_tokenizer_path(tokenizer))


    def _get_gpt2_models_list(self):
        models=listdir(constants.Sicken.models_path / "gpt2")
        if ".DS_Store" in models:
            models.remove(".DS_Store")
        return models

    def _get_gpt2_tokenizers_list(self):
        tokenizers=listdir(constants.Sicken.tokenizers_path / "gpt2")
        if ".DS_Store" in tokenizers:
            tokenizers.remove(".DS_Store")
        return tokenizers

    def _set_model(self, model):
        self._gpt2_model=GPT2LMHeadModel.from_pretrained(model, local_files_only=True)

    def _set_tokenizer(self, tokenizer):
        self._gpt2_tokenizer=GPT2Tokenizer.from_pretrained(tokenizer, local_files_only=True)

    def _get_gpt2_model_path(self, model):
        return constants.Sicken.models_path / "gpt2" /  model

    def _get_gpt2_tokenizer_path(self, tokenizer):
        return constants.Sicken.tokenizers_path / "gpt2" /  tokenizer

    def get_answer(self, message):
        features=self._gpt2_tokenizer(message['message'], return_tensors="pt")
        gen_outputs=self._gpt2_model.generate(
            **features,
            **message['parameters'] if 'parameters' in message and message['parameters'] else DEFAULT_PARAMETERS          
            )
 
        return self._gpt2_tokenizer.decode(gen_outputs[0][0])