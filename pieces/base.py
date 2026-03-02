from __future__ import annotations

import domino

from pieces.common import SecurityProtocol
from pieces.models import InputModel, SecretsModel


class BasePiece(domino.base_piece.BasePiece):

    def validate_ssl_secrets(self, input: InputModel, secrets: SecretsModel) -> None:

        if input.security_protocol == SecurityProtocol.SSL:
            if secrets is None:
                raise ValueError(
                    "Secrets must be provided when security.protocol is 'SSL'"
                )

            missing = [
                name for name, value in {
                    "ssl.ca.pem": secrets.ssl_ca_pem,
                    "ssl.certificate.pem": secrets.ssl_certificate_pem,
                    "ssl.key.pem": secrets.ssl_key_pem.get_secret_value() if secrets.ssl_key_pem else None,
                }.items()
                if value is None or value.strip() == ""
            ]

            if missing:
                raise ValueError(
                    f"When security.protocol='SSL', the following secrets must be set: "
                    f"{', '.join(missing)}"
                )

    def piece_function(self, input: InputModel, secrets: SecretsModel) -> None:
        self.validate_ssl_secrets(input, secrets)
