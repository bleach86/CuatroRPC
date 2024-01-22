"""CuatroRPC

Included classes:
- RpcClient: Rpc client class
- RpcClientAsync: ASync Rpc client class
- RpcClientCLI: Class for making RPC calls via the bitcoin-cli binary 
- RpcClientCLIAsync: Async Class for making RPC calls via the bitcoin-cli binary

Usage:
from cuatrorpc import RpcClient

rpc = RpcClient(host="localhost", username="user", password="password")

print(rpc.callrpc("getblockcount"))

"""


from cuatrorpc.cuatrorpc_rs import RpcClient, RpcClientCLI
from cuatrorpc._async_helper import RpcClientAsync, RpcClientCLIAsync


__all__ = ("RpcClient", "RpcClientCLI", "RpcClientAsync", "RpcClientCLIAsync")

if __name__ == "__main__":
    pass
