from pathlib import Path

class Sicken:
	sicken_path=Path('/opt/SickenAI')
	models_path=sicken_path / "Models"
	tokenizers_path=sicken_path / "Tokenizers"
	
class GUI:
	views_path=Sicken.sicken_path / "GUIS" / "Views"
	
class GPT2_Trainer_Constants:
	project_dir=Sicken.sicken_path
	
	models_dir=project_dir / "Models" / "GPT2"
	tokenizers_dir=project_dir/ "Tokenizers" / "GPT2"

	configs_dir=project_dir / "Trainers" / "GPT2" / "Configs"
	datasets_dir=project_dir / "Datasets"

class T5_Trainer_Constants:
	project_dir=Sicken.sicken_path
	
	models_dir=project_dir / "Models" / "T5"
	tokenizers_dir=project_dir/ "Tokenizers" / "T5"

	configs_dir=project_dir / "Trainers" / "T5" / "Configs"
	datasets_dir=project_dir / "Datasets"
	