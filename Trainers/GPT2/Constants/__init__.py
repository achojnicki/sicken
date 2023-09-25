from pathlib import Path

class GPT2_Trainer_Constants:
	project_dir=Path("/opt/Sicken AI")
	
	models_dir=project_dir / "Models" / "GPT2"
	tokenizers_dir=project_dir/ "Tokenizers" / "GPT2"

	configs_dir=project_dir / "Trainers" / "GPT2" / "Configs"
	datasets_dir=project_dir / "Datasets"
	