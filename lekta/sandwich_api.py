import os
from collections import namedtuple
from uuid import UUID

import requests

from lekta.exceptions import UnauthorizedException, LektaKernelError, ServerAvailabilityError, DialogNotFoundException

OpenResponse = namedtuple('OpenResponse', ['id', 'answer', 'language'])
DialogueResponse = namedtuple('DialogueResponse', ['answer', 'closed', 'language', 'interface'])
CloseResponse = namedtuple('CloseResponse', ['closed'])
HealthCheckResponse = namedtuple('HealthCheckResponse', ['status', 'lekta'])


class SandwichAPI:
    def __init__(self):
        self.session = requests.Session()
        self.base_api_url = os.environ.get("SANDWICH_BASE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": os.environ.get("LEKTA_API_KEY")
        }

    def open_dialogue(self) -> OpenResponse:
        try:
            data = self._lekta_request('/dialogues', {
                "language": "English",
                "interface": "Spoken",
                "operation": "Fluency",
                "context": "{\"valid\": \"json\"}"
            })
        except requests.HTTPError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                raise UnauthorizedException from exc
            elif status_code == 418:
                raise LektaKernelError from exc
            raise

        return OpenResponse(
            id=UUID(data['id']),
            answer=data['answer'],
            language=data['language']
        )

    def make_dialogue(self, uuid: UUID, text_input: str):
        try:
            data = self._lekta_request(f'/dialogues/{str(uuid)}', {
                "input": text_input,
                "context": "{\"valid\": \"json\"}"
            })
        except requests.HTTPError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                raise UnauthorizedException from exc
            elif status_code == 404:
                raise DialogNotFoundException from exc
            elif status_code == 418:
                raise LektaKernelError from exc
            raise

        return DialogueResponse(
            answer=data['answer'],
            closed=False,
            language=data['language'],
            interface=data['interface'],
        )

    def close_dialogue(self, uuid: UUID):
        try:
            self._lekta_request(f'/dialogues/{str(uuid)}/delete', {
                "context": "{\"valid\": \"json\"}"
            })
        except requests.HTTPError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                raise UnauthorizedException from exc
            elif status_code == 418:
                raise LektaKernelError from exc
            raise

        return CloseResponse(
            closed=True
        )

    def health_check(self):
        try:
            response = self.session.get(self.base_api_url + '/status')
        except Exception:
            return HealthCheckResponse(
                status='fail',
                lekta=None
            )

        return HealthCheckResponse(
            status='ok',
            lekta=response.json()['lekta']
        )

    def _lekta_request(self, path: str, payload: dict, timeout: int = 5):
        try:
            response = self.session.post(
                self.base_api_url + path,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise ServerAvailabilityError from exc

        response.raise_for_status()
        return response.json()
