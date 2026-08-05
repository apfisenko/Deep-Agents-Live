from mentor.config import PROJECT_ROOT, get_config


def test_config_loads() -> None:
    config = get_config()
    assert config.settings.openai_api_key
    assert config.settings.openai_model
    assert (PROJECT_ROOT / "config" / "settings.yaml").exists()


def test_prompt_loads() -> None:
    config = get_config()
    prompt = config.load_prompt("orchestrator")
    assert "Homework Mentor" in prompt
