from __future__ import annotations

import re
from typing import List

from pydantic import Field, field_validator

from pieces import models

# ISO8601 duration regex (simplified for PnDTnHnMn.nS, no negative durations)
ISO8601_DURATION_REGEX = re.compile(
    r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$"
)


class SecretsModel(models.SecretsModel):
    pass


class InputModel(models.InputModel):
    topics: List[str] = Field(
        title="topics",
        default=["topic.default1", "topic.default2"],
        description="Topic names",
    )

    @field_validator("topics")
    def validate_topics(cls, value: List[str]) -> List[str]:
        if value is None or len(value) == 0 or any(topic is None or topic.strip() == "" for topic in value):
            raise ValueError("topics cannot be empty, contain empty strings or None elements")
        return value

    # https://kafka.apache.org/41/configuration/consumer-configs/#consumerconfigs_client.id
    # https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html#client-id
    client_id: str = Field(
        title="client.id",
        default="test-client",
        description="An id string to pass to the server when making requests. The purpose of this is to be able to track the source of requests beyond just ip/port by allowing a logical application name to be included in server-side request logging.",
    )

    # https://kafka.apache.org/41/configuration/consumer-configs/#consumerconfigs_group.id
    # https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html#group-id
    group_id: str = Field(
        title="group.id",
        default="test-consumer-group",
        description="A unique string that identifies the consumer group this consumer belongs to. This property is required if the consumer uses either the group management functionality by using subscribe(topic) or the Kafka-based offset management strategy.",
    )

    # https://kafka.apache.org/41/configuration/consumer-configs/#consumerconfigs_auto.offset.reset
    # https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html#auto-offset-reset
    auto_offset_reset: str = Field(
        title="auto.offset.reset",
        default="latest",
        description="""What to do when there is no initial offset in Kafka or if the current offset does not exist any more on the server (e.g. because that data has been deleted):
earliest: automatically reset the offset to the earliest offset
latest: automatically reset the offset to the latest offset
by_duration:<duration>: automatically reset the offset to a configured <duration> from the current timestamp. <duration> must be specified in ISO8601 format (PnDTnHnMn.nS). Negative duration is not allowed.
none: throw exception to the consumer if no previous offset is found for the consumer's group
anything else: throw exception to the consumer."""
        ,
    )

    @field_validator("auto_offset_reset", mode="before")
    def validate_auto_offset_reset(cls, value: str) -> str:
        v_lower = value.lower()
        allowed_literals = {"latest", "earliest", "none"}

        if v_lower in allowed_literals:
            return v_lower

        # Check for pattern "by_duration:<duration>"
        if v_lower.startswith("by_duration:"):
            duration_str = v_lower[len("by_duration:"):]
            if not ISO8601_DURATION_REGEX.match(duration_str):
                raise ValueError(
                    f"Invalid ISO8601 duration format in auto_offset_reset: {duration_str}"
                )
            return f"by_duration:{duration_str}"  # preserve the original pattern

        raise ValueError(
            f"Invalid auto_offset_reset value: {value}. Must be one of "
            f"{allowed_literals} or by_duration:<ISO8601 duration>"
        )

    poll_timeout: float = Field(
        title="poll.timeout",
        default=60,
        description="Timeout in seconds for polling messages.",
    )

    @field_validator("poll_timeout")
    def validate_poll_timeout(cls, value, info):
        if value <= 0:
            raise ValueError("poll_timeout must be greater than 0")
        return value

    msg_value_encoding: str = Field(
        title="msg.value.encoding",
        default="utf-8",
        description="Encoding of messages",
    )


class OutputModel(models.OutputModel):
    messages_file_path: str = Field(
        title="messages.file.path",
        description="File with consumed messages."
    )
    topics: List[str] = Field(
        title="topics",
        description="Topic name",
    )
    group_id: str = Field(
        title="group.id",
        description="Kafka consumer group",
    )
    msg_value_encoding: str = Field(
        title="msg.value.encoding",
        description="Encoding of messages; i.e., 'utf-8', 'base64'",
    )
