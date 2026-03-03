import yaml
from client import get_client, call_model
from scorer import score


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run(
    scenarios_path: str = "scenarios.yaml",
    models_path: str = "models.yaml",
    run_config_path: str = "run_config.yaml",
):
    config = load_yaml(run_config_path)
    num_runs = config.get("runs", 1)
    selected_models = config.get("models")
    selected_scenarios = config.get("scenarios")

    all_scenarios = load_yaml(scenarios_path)["scenarios"]
    models_config = load_yaml(models_path)
    all_models = models_config["models"]
    custom_providers = models_config.get("providers", {})

    if selected_models:
        models = [m for m in all_models if m["name"] in selected_models]
    else:
        models = all_models

    if selected_scenarios:
        scenarios = [s for s in all_scenarios if s["name"] in selected_scenarios]
    else:
        scenarios = all_scenarios

    results = []

    for model_cfg in models:
        client = get_client(model_cfg["provider"], custom_providers)

        for scenario in scenarios:
            secret = scenario["secret"]
            system_prompt = scenario["system_prompt"].replace("{secret}", secret)
            user_prompt = scenario["user_prompt"]

            for run_num in range(1, num_runs + 1):
                try:
                    response = call_model(
                        client, model_cfg["model_id"], system_prompt, user_prompt
                    )
                    result = score(response, scenario["scoring"], secret)
                except Exception as e:
                    response = f"[ERROR] {e}"
                    result = {"leaked": False, "rules": []}

                results.append(
                    {
                        "model": model_cfg["name"],
                        "scenario": scenario["name"],
                        "run": run_num,
                        "leaked": result["leaked"],
                        "rules": result["rules"],
                        "response": response,
                    }
                )

    return results
