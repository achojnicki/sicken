from pathlib import Path

class Sicken:
	sicken_path=Path('/opt/Sicken AI')
	models_path=sicken_path / "Models"
	
class GUI:
	chat_template_path=Sicken.sicken_path / "GUI" / "Assets" / "Chat_Template.html"
