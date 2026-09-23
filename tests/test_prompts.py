from prompts.system_prompt import PROMPT_V1, PROMPT_V2, get_system_prompt


def test_all_prompt_versions_are_available():
    assert "maquinas de coser" in PROMPT_V1
    assert "ROL" in PROMPT_V2
    assert "<reglas>" in get_system_prompt("V3")
    assert "<ejemplos>" in get_system_prompt("V3")


def test_v3_handles_unknown_and_out_of_domain():
    prompt = get_system_prompt("V3")
    assert "No inventes" in prompt
    assert "fuera del dominio" in prompt
    assert "olor a quemado" in prompt

