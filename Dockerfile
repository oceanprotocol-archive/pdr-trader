##
## Copyright 2023 Ocean Protocol Foundation
## SPDX-License-Identifier: Apache-2.0
##
FROM python:3.8
LABEL maintainer="Ocean Protocol <devops@oceanprotocol.com>"
COPY . /pdr-trader
WORKDIR /pdr-trader
RUN pip install -r requirements.txt
ENV ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
ENV RPC_URL="http://127.0.0.1:8545"
ENV SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
ENV PRIVATE_KEY="0x8467415bb2ba7c91084d932276214b11a3dd9bdb2930fefa194b666dd8020b99"
ENV WAIT_FOR_SUBGRAPH=false
ENTRYPOINT ["/pdr-trader/docker-entrypoint.sh"]
