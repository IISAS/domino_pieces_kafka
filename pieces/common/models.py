from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel, Field, SecretStr
from pydantic import field_validator

from .enums import SecurityProtocol


class SecretsModel(BaseModel):
    ssl_ca_pem: Optional[str] = Field(
        title="ssl.ca.pem",
        default=None,
        description="CA certificate in PEM format as a single line string with new line characters replaced with \\n.",
    )
    ssl_certificate_pem: Optional[str] = Field(
        title="ssl.certificate.pem",
        default=None,
        description="Client's certificate in PEM format as a single line string with new line characters replaced with \\n."
    )
    ssl_key_pem: Optional[SecretStr] = Field(
        title="ssl.key.pem",
        default=None,
        description="Client's private key in PEM format as a single line string with new line characters replaced with \\n.",
    )


class InputModel(BaseModel):
    bootstrap_servers: List[str] = Field(
        title="bootstrap.servers",
        default=["127.0.0.1:9093"],
        description="Kafka broker addresses",
    )

    # https://kafka.apache.org/41/configuration/consumer-configs/#consumerconfigs_security.protocol
    # https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html#security-protocol
    security_protocol: SecurityProtocol = Field(
        title=SecurityProtocol.title(),
        default=SecurityProtocol.PLAINTEXT,
        description="Protocol used to communicate with brokers.",
    )

    @field_validator("security_protocol")
    def validate_security_protocol(cls, value: str) -> str:
        allowed = SecurityProtocol.values()
        normalized = value.upper()  # normalize to uppercase
        if normalized not in allowed:
            raise ValueError(f"Invalid security protocol: {value}. Must be one of (case insensitive) {allowed}")
        return normalized  # return normalized value

    # https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html#ssl-endpoint-identification-algorithm
    # https://kafka.apache.org/41/configuration/producer-configs/#producerconfigs_ssl.endpoint.identification.algorithm
    ssl_endpoint_identification_algorithm: str = Field(
        title="ssl.endpoint.identification.algorithm",
        default="none",
        description="The endpoint identification algorithm to validate server hostname using server certificate.",
    )


class OutputModel(BaseModel):
    bootstrap_servers: List[str] = Field(
        title="bootstrap.servers",
        description="Kafka broker addresses",
    )
    security_protocol: SecurityProtocol = Field(
        title=SecurityProtocol.title(),
        description="Protocol used to communicate with brokers.",
    )
    ssl_endpoint_identification_algorithm: str = Field(
        title="ssl.endpoint.identification.algorithm",
        description="The endpoint identification algorithm to validate server hostname using server certificate.",
    )
