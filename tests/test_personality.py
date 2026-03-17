from leah.personality import get_system_prompt, SYSTEM_PROMPT_TEMPLATE


def test_system_prompt_renders():
    prompt = get_system_prompt(timezone="America/New_York", name="Pat")
    assert "Leah" in prompt
    assert "Pat" in prompt
    assert "America/New_York" in prompt
    # Should not contain unformatted placeholders
    assert "{timezone}" not in prompt
    assert "{name}" not in prompt
    assert "{now}" not in prompt


def test_system_prompt_forbids_filler_phrases():
    prompt = get_system_prompt(timezone="UTC", name="User")
    # The prompt should instruct Leah to avoid filler phrases, not use them
    assert "Never start" in prompt or "never" in prompt.lower()
    assert "Certainly" in prompt  # referenced as a banned phrase
    assert "happy to help" in prompt  # referenced as banned


def test_system_prompt_includes_tool_capabilities():
    prompt = get_system_prompt(timezone="UTC", name="User")
    assert "Gmail" in prompt
    assert "Calendar" in prompt
    assert "Tasks" in prompt
    assert "Drive" in prompt
