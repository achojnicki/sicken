from pathlib import Path

class T5_Trainer_Constants:
	project_dir=Path("/opt/Sicken AI")
	
	models_dir=project_dir / "Models" / "T5"
	tokenizers_dir=project_dir/ "Tokenizers" / "T5"

	configs_dir=project_dir / "Trainers" / "T5" / "Configs"
	datasets_dir=project_dir / "Datasets"
	