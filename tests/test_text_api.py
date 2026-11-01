import pytest
from fastapi.testclient import TestClient

from app import agent
from app.main import app

client = TestClient(app)


@pytest.fixture
def override_annotation():
    from app.main import get_annotator
    async def annotate(request):
        return agent.TextAnalysisResponse(
            transcript=request.transcript, segments=[request.transcript],
            boundary_positions=[], prosody_status='not_supplied')
    app.dependency_overrides[get_annotator] = lambda: annotate
    yield get_annotator
    app.dependency_overrides.clear()


def test_text_endpoint_displays_structured_result(override_annotation):
    response = client.post('/analyze-text', json={'transcript': 'A toy robot waved.'})
    assert response.status_code == 200
    assert response.json() == {
        'transcript': 'A toy robot waved.', 'segments': ['A toy robot waved.'],
        'boundary_positions': [], 'prosody_status': 'not_supplied'}


@pytest.mark.parametrize('payload', [{}, {'transcript': ' '},
                                    {'transcript': 'x' * 5001},
                                    {'transcript': 'Hi.', 'prosodic_cues': 'x' * 5001}])
def test_invalid_input_never_calls_annotator(override_annotation, payload):
    async def forbidden(request):
        pytest.fail('Invalid input reached annotation')
    app.dependency_overrides[override_annotation] = lambda: forbidden
    assert client.post('/analyze-text', json=payload).status_code == 422


@pytest.mark.parametrize(('error_name', 'status'), [
    ('AnnotationUnavailable', 503), ('AnnotationTimedOut', 504),
    ('AnnotationFailed', 502), ('AnnotationInvalid', 502),
])
def test_errors_are_sanitized(override_annotation, error_name, status):
    async def fail(request):
        raise getattr(agent, error_name)('synthetic-secret-provider-detail')
    app.dependency_overrides[override_annotation] = lambda: fail
    response = client.post('/analyze-text', json={'transcript': 'A toy robot waved.'})
    assert response.status_code == status
    assert 'synthetic-secret-provider-detail' not in response.text


def test_audio_placeholder_remains_unchanged():
    response = client.post('/analyze', files={'audio': ('synthetic.wav', b'test', 'audio/wav')})
    assert response.status_code == 200
    assert set(response.json()) == {'transcript', 'prosodic_features', 'as_unit_annotation'}
    assert all('Placeholder' in value for value in response.json().values())
