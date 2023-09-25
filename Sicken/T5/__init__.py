from os import listdir
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import Constants

class Sicken:
    def __init__(self, root):
        self.root=root
        self.log=root.log

        self.set_model()
        self.set_tokenizer()

    def get_t5_models_list(self):
        models=listdir(Constants.Sicken.models_path / "T5")
        if ".DS_Store" in models:
            models.remove(".DS_Store")
        return models

    def get_t5_tokenizers_list(self):
        tokenizers=listdir(Constants.Sicken.tokenizers_path / "T5")
        if ".DS_Store" in tokenizers:
            tokenizers.remove(".DS_Store")
        return tokenizers

    def set_model(self):
        self.t5_model=AutoModelForSeq2SeqLM.from_pretrained(self.get_t5_model(), local_files_only=True)

    def set_tokenizer(self):
        self.t5_tokenizer=AutoTokenizer.from_pretrained(self.get_t5_tokenizer(), local_files_only=True)

    def get_t5_model(self):
        model=self.root.gui.get_selected_model() if hasattr(self.root,'gui') else self.get_t5_models_list()[0]
        return Constants.Sicken.models_path / "T5" /  model

    def get_t5_tokenizer(self):
        tokenizer=self.root.gui.get_selected_tokenizer() if hasattr(self.root,'gui') else self.get_t5_tokenizers_list()[0]
        return Constants.Sicken.tokenizers_path / "T5" /  tokenizer

    def get_answer(self, question):
        d=[]
        features=self.t5_tokenizer(question, return_tensors="pt")
        gen_outputs=self.t5_model.generate(features.input_ids, attention_mask=features.attention_mask, max_new_tokens=100000)
        for a in gen_outputs:
            d.append(self.t5_tokenizer.decode(a, skip_special_tokens=True))
        return d