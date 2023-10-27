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
"""The Python implementation of the GRPC helloworld.Greeter server."""
import json
import os.path
import pathlib
import typing
from concurrent import futures
import logging
import shutil
import grpc
working_dir = pathlib.Path(__file__).parent.__str__()
app_dir = pathlib.Path(__file__).parent.parent.__str__()
proto_file = os.path.join(working_dir,"command.proto")
run_proto_file = os.path.join(app_dir,"command.proto")
if not os.path.isfile(run_proto_file):
    shutil.copy(proto_file,run_proto_file)

protos, services = grpc.protos_and_services("command.proto")


class Commander(services.CommanderServicer):
    def __init__(self,handler):
        if not callable(handler):
            raise Exception("handler must a function with one dict arg")
        self.handler = handler
    def Exec(self, request, context):
        data = json.loads(request.JSONText)
        res_data = self.handler(data,context)
        return protos.CommandReply(JSONText=json.dumps(res_data))


def start_serverles(port:int,handler:typing.Callable):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    services.add_CommanderServicer_to_server(Commander(handler), server)
    # server.add_insecure_port("[::]:50051")
    server.add_insecure_port(f"0.0.0.0:{port}")

    server.start()
    server.wait_for_termination()
