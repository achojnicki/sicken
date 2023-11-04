from pathlib import Path

class Sicken:
	sicken_path=Path('/opt/sicken')
	models_path=sicken_path / "models"
	tokenizers_path=sicken_path / "tokenizers"
	
class GUI:
	views_path=Sicken.sicken_path / "sickenschat" / "views"
	
class GPT2_Trainer_Constants:
	project_dir=Sicken.sicken_path
	
	models_dir=project_dir / "models" / "gpt2"
	tokenizers_dir=project_dir/ "tokenizers" / "gpt2"

	configs_dir=project_dir / "trainers" / "gpt2" / "configs"
	datasets_dir=project_dir / "sickens_datasets"

class T5_Trainer_Constants:
	project_dir=Sicken.sicken_path
	
	models_dir=project_dir / "models" / "t5"
	tokenizers_dir=project_dir/ "tokenizers" / "t5"

	configs_dir=project_dir / "trainers" / "t5" / "configs"
	datasets_dir=project_dir / "sickens_datasets"
	
class Generator_Constants:
	system_message="Your task is to provide the steps requested by the user."
	test_resp=[{"actions_group": "Terminal", "action": "print_to_terminal", "data": {"data":"test123"}},{"actions_group": "Terminal", "action": "print_to_terminal", "data": {"data":"test123"}}]

