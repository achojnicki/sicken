from pathlib import Path

class Sicken:
	sicken_path=Path('/opt/Sicken AI')
	models_path=sicken_path / "Models"
	tokenizers_path=sicken_path / "Tokenizers"
	
class GUI:
	views_path=Sicken.sicken_path / "GUI" / "Views"
	
