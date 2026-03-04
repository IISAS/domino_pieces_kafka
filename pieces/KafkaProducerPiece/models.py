from typing import List

from common import models
from common.enums import Acks
from pydantic import Field


class SecretsModel(models.SecretsModel):
    pass


class InputModel(models.InputModel):
    # https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html#acks
    # https://kafka.apache.org/41/configuration/producer-configs/#producerconfigs_acks
    acks_raw: Acks = Field(
        title=Acks.title(),
        default=Acks.all,
        description="The number of acknowledgments the producer requires the leader to have received before considering a request complete.",
    )

    @property
    def acks(self) -> str:
        return {
            Acks.fire_and_forget: "0",
            Acks.wait_for_leader: "1",
            Acks.all: "all",
        }[self.acks_raw]

    # https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html#enable-idempotence
    # https://kafka.apache.org/41/configuration/producer-configs/#producerconfigs_enable.idempotence
    enable_idempotence_bool: bool = Field(
        title="enable.idempotence",
        default=True,
        description="Whether to ensure that exactly one copy of each message is written in the stream.",
    )

    @property
    def enable_idempotence(self) -> str:
        return str(self.enable_idempotence_bool)

    messages_file_path: str = Field(
        title="messages.file.path",
        default="messages.jsonl",
        description="Path to a file containing messages to produce by this producer.",
    )


class OutputModel(models.OutputModel):
    topics: List[str] = Field(
        title="topics",
        description="Topic name",
    )
    num_produced_messages: int = Field(
        title="num.produced.messages",
        description="The number of produced messages."
    )
