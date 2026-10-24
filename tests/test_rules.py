from app.rules import select_saved_fields


def test_retains_only_proposal_fields():
    record = {
        "transcript": "Hello.",
        "prosodic_features": "pause=0.5",
        "as_unit_annotation": "Hello. |",
        "audio": b"raw audio data",
    }
    assert select_saved_fields(record) == {
        "transcript": "Hello.",
        "prosodic_features": "pause=0.5",
        "as_unit_annotation": "Hello. |",
    }


def test_audio_alone_is_not_retained():
    assert select_saved_fields({"audio": b"raw audio data"}) == {}
