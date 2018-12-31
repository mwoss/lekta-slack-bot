from collections import namedtuple
from os import environ
from uuid import UUID

import requests

from slack_bot.lekta.exceptions import (UnauthorizedException, LektaKernelError,
                                        DialogNotFoundException, ServerAvailabilityError)

OpenResponse = namedtuple('OpenResponse', ['uuid', 'answer', 'language'])
DialogueResponse = namedtuple('DialogueResponse', ['answer', 'closed', 'language', 'interface'])
CloseResponse = namedtuple('CloseResponse', ['closed'])
HealthCheckResponse = namedtuple('HealthCheckResponse', ['status', 'response_body'])


class SandwichAPI:
    def __init__(self):
        self.session = requests.Session()
        self.base_api_url = environ.get("SANDWICH_BASE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": environ.get("LEKTA_API_KEY")
        }

    def open_dialogue(self) -> OpenResponse:
        response = self._lekta_request('/dialogues', {
            "language": "English",
            "interface": "Spoken",
            "operation": "Fluency",
            "context": "{\"valid\": \"json\"}"
        })

        data = response.json()
        return OpenResponse(
            uuid=UUID(data['id']),
            answer=data['answer'],
            language=data['language']
        )

    def make_dialogue(self, uuid: UUID, text_input: str) -> DialogueResponse:
        response = self._lekta_request(f'/dialogues/{str(uuid)}', {
            "input": text_input,
            "context": "{\"valid\": \"json\"}"
        })

        data = response.json()
        return DialogueResponse(
            answer=data['answer'],
            closed=False,
            language=data['language'],
            interface=data['interface'],
        )

    def close_dialogue(self, uuid: UUID) -> CloseResponse:
        self._lekta_request(f'/dialogues/{str(uuid)}/delete', {
            "context": "{\"valid\": \"json\"}"
        })

        return CloseResponse(closed=True)

    def health_check(self) -> HealthCheckResponse:
        try:
            response = self.session.get(self.base_api_url + '/status')
        except (requests.ConnectionError, requests.HTTPError) as exc:
            return HealthCheckResponse(status='fail', response_body=str(exc))

        return HealthCheckResponse(status='ok', response_body=response.json()['lekta'])

    def _lekta_request(self, path: str, payload: dict, timeout: int = 5) -> requests.Response:
        try:
            response = self.session.post(
                self.base_api_url + path,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise ServerAvailabilityError from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                raise UnauthorizedException(status_code) from exc
            elif status_code == 404:
                raise DialogNotFoundException(status_code) from exc
            elif status_code == 418:
                raise LektaKernelError(status_code) from exc

            raise ServerAvailabilityError("Sandwich API had internal error")

        return response
