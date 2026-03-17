from leah.memory import ConversationMemory


def test_add_and_get():
    mem = ConversationMemory()
    mem.add_user("hello")
    mem.add_assistant("hi")
    msgs = mem.get_messages()
    assert len(msgs) == 2
    assert msgs[0] == {"role": "user", "content": "hello"}
    assert msgs[1] == {"role": "assistant", "content": "hi"}


def test_tool_results_added_as_user_role():
    mem = ConversationMemory()
    mem.add_user("do something")
    mem.add_assistant([{"type": "tool_use", "id": "x", "name": "foo", "input": {}}])
    mem.add_tool_results([{"type": "tool_result", "tool_use_id": "x", "content": "done"}])
    msgs = mem.get_messages()
    assert msgs[2]["role"] == "user"
    assert msgs[2]["content"][0]["type"] == "tool_result"


def test_trim_at_limit():
    mem = ConversationMemory(max_messages=4)
    for i in range(3):
        mem.add_user(f"user {i}")
        mem.add_assistant(f"assistant {i}")
    # 6 messages added, limit is 4 — oldest 2 should be gone
    msgs = mem.get_messages()
    assert len(msgs) == 4
    assert msgs[0]["content"] == "user 1"


def test_clear():
    mem = ConversationMemory()
    mem.add_user("test")
    mem.clear()
    assert mem.get_messages() == []
    assert len(mem) == 0


def test_len():
    mem = ConversationMemory()
    assert len(mem) == 0
    mem.add_user("a")
    assert len(mem) == 1
