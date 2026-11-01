"""Run with the environment's Playwright Python; all HTTP responses are local mocks.

python tests/browser_text_review.py
"""

import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def check_text_review():
    html = (Path(__file__).resolve().parents[1] / 'app/page.html').read_text()
    text = '😀 A toy waved. <img src=x onerror=alert(1)> stayed still.'
    segments = ['😀 A toy waved. ', '<img src=x onerror=alert(1)> stayed still.']
    requests = []
    failures = []
    state = {'fail': False}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium',
                                             headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(3000)
        page.on('pageerror', lambda error: failures.append(str(error)))

        def respond(route):
            path = route.request.url.split('http://synthetic.test', 1)[-1]
            if path == '/':
                route.fulfill(status=200, content_type='text/html', body=html)
            elif path == '/analyze-text':
                requests.append(route.request.post_data_json)
                if state['fail']:
                    route.fulfill(status=502, content_type='application/json',
                                  body=json.dumps({'detail': 'synthetic-secret-provider-detail'}))
                else:
                    route.fulfill(status=200, content_type='application/json', body=json.dumps({
                        'transcript': text, 'segments': segments,
                        'boundary_positions': [15], 'prosody_status': 'not_supplied'}))
            elif path == '/analyze':
                route.fulfill(status=200, content_type='application/json', body=json.dumps({
                    'transcript': '[Placeholder transcript]',
                    'prosodic_features': '[Placeholder prosody]',
                    'as_unit_annotation': '[Placeholder annotation]'}))
            else:
                route.abort()

        page.route('**/*', respond)
        page.goto('http://synthetic.test/')
        expect(page.get_by_text('Synthetic data only.', exact=False)).to_be_visible()
        page.locator('#text-transcript').fill(text)
        page.locator('#text-form button').click()
        expect(page.locator('#text-status')).to_have_text('AI suggestions received. Review before use.')
        assert requests == [{'transcript': text, 'prosodic_cues': None}]
        expect(page.locator('#text-segments')).to_have_text(' | '.join(segments))
        assert page.locator('#text-segments img').count() == 0
        expect(page.locator('#text-prosody')).to_contain_text('not supplied')
        expect(page.locator('#position-note')).to_have_text(
            'UI character positions only; not research word-level boundary positions.')
        expect(page.locator('#boundary-list')).to_contain_text('15')
        expect(page.locator('#boundary-list')).to_contain_text('waved.')
        original = page.locator('#boundary-list').inner_text()
        page.locator('#text-review').fill('A synthetic human correction.')
        expect(page.locator('#review-status')).to_contain_text('Edited locally')
        expect(page.locator('#edit-note')).to_have_text(
            'Original AI boundary positions remain unchanged after edits; they are not recalculated.')
        assert page.locator('#boundary-list').inner_text() == original
        state['fail'] = True
        page.locator('#text-form button').click()
        expect(page.locator('#text-status')).to_contain_text('temporarily unavailable')
        assert 'synthetic-secret-provider-detail' not in page.locator('#text-status').inner_text()
        expect(page.locator('#boundary-list')).to_be_empty()
        expect(page.locator('#text-review')).to_be_disabled()
        expect(page.locator('#text-form button')).to_be_enabled()
        page.locator('#audio').set_input_files({'name': 'synthetic.wav',
                                              'mimeType': 'audio/wav', 'buffer': b'test'})
        page.locator('#analysis-form button').click()
        expect(page.locator('#status')).to_contain_text('No audio was analyzed.')
        expect(page.locator('#transcript')).to_have_text('[Placeholder transcript]')
        assert not failures
        browser.close()
    print('Browser check passed: Unicode, literal HTML, missing cues, local edits, '
          'unchanged positions, safe failure, and audio placeholder.')


if __name__ == '__main__':
    check_text_review()
