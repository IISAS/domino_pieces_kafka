from __future__ import annotations

from domino.base_piece import BasePiece as DominoBasePiece

from .common import SecurityProtocol
from .models import InputModel, SecretsModel


class BasePiece(DominoBasePiece):

    def validate_ssl_secrets(self, input_data: InputModel, secrets_data: SecretsModel) -> None:

        if input_data.security_protocol == SecurityProtocol.SSL:
            if secrets_data is None:
                raise ValueError(
                    "Secrets must be provided when security.protocol is 'SSL'"
                )

            missing = [
                name for name, value in {
                    "ssl.ca.pem": secrets_data.ssl_ca_pem,
                    "ssl.certificate.pem": secrets_data.ssl_certificate_pem,
                    "ssl.key.pem": secrets_data.ssl_key_pem.get_secret_value() if secrets_data.ssl_key_pem else None,
                }.items()
                if value is None or value.strip() == ""
            ]

            if missing:
                raise ValueError(
                    f"When security.protocol='SSL', the following secrets must be set: "
                    f"{', '.join(missing)}"
                )

    def piece_function(self, input_data: InputModel, secrets_data: SecretsModel) -> None:
        self.validate_ssl_secrets(input_data, secrets_data)
