# Copyright 2020 The gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Hello World without using protoc.

This example parses message and service schemas directly from a
.proto file on the filesystem.

Several APIs used in this example are in an experimental state.
"""
import json
import pathlib
import time

working_dir = pathlib.Path(__file__).parent.__str__()
import sys
sys.path.append("/app")
sys.path.append(working_dir)

import logging

import grpc
import grpc.experimental

# NOTE: The path to the .proto file must be reachable from an entry
# on sys.path. Use sys.path.insert or set the $PYTHONPATH variable to
# import from files located elsewhere on the filesystem.

protos = grpc.protos("command.proto")
services = grpc.services("command.proto")




def rpc_call(server:str,port:int, data:dict)->dict:
    response = services.Commander.Exec(
        protos.CommandRequest(JSONText=json.dumps(data)), f"{server}:{port}", insecure=True
    )
    return  json.dumps(response.JSONText)


while True:
    i = 0
    fx = rpc_call("localhost", 50011, data=dict(
        name=f"code{i}",
        code="dasdas"
    ))
    print(fx)
    time.sleep(5)
    i += 1

