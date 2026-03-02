import base64
import json
import os
import tempfile
import time
from pathlib import Path

from confluent_kafka import KafkaError
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic, KafkaException

from pieces.base import BasePiece
from .models import InputModel, OutputModel, SecretsModel


def decode_msg_value(msg_value, encoding):
    if msg_value is None:
        return None
    if encoding == "base64":
        return base64.b64decode(msg_value)
    elif encoding == "utf-8":
        return msg_value.decode('utf-8')
    return msg_value


class KafkaTopicCreatorPiece(BasePiece):

    def piece_function(
        self,
        input: InputModel,
        secrets: SecretsModel
    ):
        self.super().piece_function(input, secrets)

        self.logger.info("Creating topics...")
        start_time = time.time()

        with tempfile.TemporaryDirectory() as tmp_dir:

            self.validate_ssl_secrets(input, secrets)

            admin_client_conf = {
                # 'debug': 'security,broker,conf',
                # 'log_level': 7,
                'bootstrap.servers': ','.join(input.bootstrap_servers),
                **(
                    {
                        'security.protocol': input.security_protocol,
                        'ssl.ca.pem': secrets.ssl_ca_pem.replace("\\n", "\n"),
                        'ssl.certificate.pem': secrets.ssl_certificate_pem.replace("\\n", "\n"),
                        'ssl.key.pem': secrets.ssl_key_pem.get_secret_value().replace("\\n", "\n"),
                        'ssl.endpoint.identification.algorithm': input.ssl_endpoint_identification_algorithm,
                    } if input.security_protocol is not None
                         and input.security_protocol.lower().strip() == 'ssl'
                    else {}
                ),
            }

            admin = AdminClient(conf=admin_client_conf)

            new_topics = [
                NewTopic(
                    topic=topic_name,
                    num_partitions=input.num_partitions,
                    replication_factor=input.replication_factor,
                    config={
                        "cleanup.policy": ','.join(input.cleanup_policy),
                        "retention.ms": input.retention_ms,
                        "min.insync.replicas": input.min_insync_replicas,
                    },
                ) for topic_name in input.topics
            ]

            topics_created = []
            futures = admin.create_topics(new_topics)
            for topic, future in futures.items():
                try:
                    future.result()
                    topics_created.append(topic)
                except KafkaException as e:
                    if e.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS and input.exists_ok:
                        self.logger.warning(f"Topic '{topic}' already exists.")
                        topics_created.append(topic)
                        pass
                    else:
                        self.logger.error(f"Could not create topic '{topic}': {e}")
                        raise e

            duration = time.time() - start_time

            result = {
                "topics_created": topics_created,
                "duration": duration,
            }

            result_file_path = os.path.join(Path(self.results_path), "result.json")
            with open(result_file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f)

            # Set display result
            self.display_result = {
                "file_type": "json",
                "file_path": result_file_path,
            }

            # Return output
            return OutputModel(
                bootstrap_servers=input.bootstrap_servers,
                security_protocol=input.security_protocol,
                topics_created=topics_created,
            )
