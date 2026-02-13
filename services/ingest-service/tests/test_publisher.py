from app.publisher import InMemoryPublisher, event_partition_key


def test_partition_key_is_stable() -> None:
    assert event_partition_key("p-42", "proc-17") == "p-42:proc-17"


def test_in_memory_publisher_collects_messages() -> None:
    pub = InMemoryPublisher()
    pub.publish("topic", "key", {"x": 1})

    assert len(pub.messages) == 1
    assert pub.messages[0]["topic"] == "topic"
    assert pub.messages[0]["key"] == "key"
    assert pub.messages[0]["payload"]["x"] == 1
