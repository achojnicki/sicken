from pathlib import Path

class Sicken:
	sicken_path=Path('/opt/Sicken AI')
	models_path=sicken_path / "Models"
	tokenizers_path=sicken_path / "Tokenizers"
	
class GUI:
	chat_template_t5_path=Sicken.sicken_path / "GUI" / "Assets" / "Chat_Template_T5.html"
	chat_template_gpt2_path=Sicken.sicken_path / "GUI" / "Assets" / "Chat_Template_GPT2.html"
	
