from sicken import constants

from os import listdir
from transformers import T5ForConditionalGeneration, AutoTokenizer

DEFAULT_PARAMETERS={
    #"max_new_tokens":100000,
    "num_beams":32,
    "min_length":20,
    "max_length":2000,
    "temperature":0.76,
    "do_sample":True,
    "early_stopping":True,
    "no_repeat_ngram_size":2,
    "length_penalty":1
}

class Sicken:
    def __init__(self, root, model, tokenizer):
        self._root=root
        self._log=root._log

        self._set_model(self._get_t5_model_path(model))
        self._set_tokenizer(self._get_t5_tokenizer_path(tokenizer))

    def _get_t5_models_list(self):
        models=listdir(constants.Sicken.models_path / "t5")
        if ".DS_Store" in models:
            models.remove(".DS_Store")
        return models

    def _get_t5_tokenizers_list(self):
        tokenizers=listdir(constants.Sicken.tokenizers_path / "t5")
        if ".DS_Store" in tokenizers:
            tokenizers.remove(".DS_Store")
        return tokenizers

    def _set_model(self, model):
        self.t5_model=T5ForConditionalGeneration.from_pretrained(model, local_files_only=True)

    def _set_tokenizer(self, tokenizer):
        self.t5_tokenizer=AutoTokenizer.from_pretrained(tokenizer, local_files_only=True)

    def _get_t5_model_path(self, model_name):
        return constants.Sicken.models_path / "t5" /  model_name

    def _get_t5_tokenizer_path(self,tokenizer_name):
        return constants.Sicken.tokenizers_path / "t5" /  tokenizer_name

    def get_answer(self, message):

        features=self.t5_tokenizer(message['message'], return_tensors="pt")
        gen_outputs=self.t5_model.generate(
            **features,
            **message['parameters'] if 'parameters' in message and message['parameters'] else DEFAULT_PARAMETERS
            )

            
        return self.t5_tokenizer.decode(gen_outputs[0], skip_special_tokens=True)