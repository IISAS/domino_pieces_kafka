FROM ghcr.io/iisas/domino-base-piece:latest

# Install specific requirements to run ShellExecute Piece
RUN apt-get update
RUN apt install net-tools

# Need to copy pieces source code
COPY config.toml /home/domino/pieces_repository/
COPY pieces /home/domino/pieces_repository/pieces
COPY .domino /home/domino/pieces_repository/.domino

COPY dependencies/requirements_kafka.txt /home/domino/pieces_repository/dependencies/
RUN pip install --no-cache-dir -r /home/domino/pieces_repository/dependencies/requirements_kafka.txt

ENV PYTHONPATH="/home/domino/pieces_repository:${PYTHONPATH}"