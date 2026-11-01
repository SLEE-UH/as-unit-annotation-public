import pytest

from app import rules


@pytest.mark.parametrize(('text', 'segments', 'expected'), [
    ('Hi. Bye.', ['Hi. ', 'Bye.'], [4]),
    ('Hi.', ['Hi.'], []),
    ('Go. Go.', ['Go. ', 'Go.'], [4]),
    ('😀 Hi. Bye.', ['😀 Hi. ', 'Bye.'], [6]),
    (' Hi.\nBye. ', [' Hi.\n', 'Bye. '], [5]),
])
def test_exact_boundaries(text, segments, expected):
    assert rules.boundary_offsets(text, segments) == expected


@pytest.mark.parametrize('segments', [[], [''], ['Hi.', ''], ['Hi.'],
                                      ['Hi.', 'Bye.'], ['Hello. ', 'Bye.']])
def test_rejects_missing_rewritten_or_empty_segments(segments):
    with pytest.raises(ValueError):
        rules.boundary_offsets('Hi. Bye.', segments)
