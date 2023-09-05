from os import listdir
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import Constants

class Sicken:
    def __init__(self, root):
        self.root=root
        self.log=root.log

        self.set_models_tokenizers()

    def get_t5_models_list(self):
        models=listdir(Constants.Sicken.models_path / "T5")
        if ".DS_Store" in models:
            models.remove(".DS_Store")
        return models


    def set_models_tokenizers(self):
        self.t5_model=AutoModelForSeq2SeqLM.from_pretrained(self.get_t5_model(), local_files_only=True)
        self.t5_tokenizer=AutoTokenizer.from_pretrained(self.get_t5_model(), local_files_only=True)

    def get_t5_model(self):
        model=self.root.gui.get_selected_model() if hasattr(self.root,'gui') else self.get_t5_models_list()[0]
        return Constants.Sicken.models_path / "T5" /  model

    def get_answer(self, question):
        d=[]
        input_ids=self.t5_tokenizer(question, return_tensors="pt").input_ids
        gen_outputs=self.t5_model.generate(input_ids, max_new_tokens=100000)
        for a in gen_outputs:
            d.append(self.t5_tokenizer.decode(a, skip_special_tokens=True))
        return d