##
## Copyright 2023 Ocean Protocol Foundation
## SPDX-License-Identifier: Apache-2.0
##
FROM ubuntu:20.04
LABEL maintainer="Ocean Protocol <devops@oceanprotocol.com>"

ARG VERSION

RUN apt-get update && \
   apt-get install --no-install-recommends -y \
   python3.8 \
   python3-pip \
   python3.8-dev \
   gettext-base

COPY . /pdr-trader
WORKDIR /pdr-trader

RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt

ENV ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
ENV RPC_URL="http://127.0.0.1:8545"
ENV SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
ENV PRIVATE_KEY="0x8467415bb2ba7c91084d932276214b11a3dd9bdb2930fefa194b666dd8020b99"

ENTRYPOINT ["python3","main.py"]
