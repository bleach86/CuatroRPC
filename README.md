# CuatroRPC

Fast Bitcoin RPC Client Library for Python leveraging Rust.

CuatroRPC aims to be a simple and fast RPC Client for Bitcoin compatible RPC servers.

## Installation

Installation can be done with pip.

```
pip install cuatrorpc
```

## Usage

```
from cuatrorpc import RpcClient

rpc = RpcClient(username="username", password="password", port=8033)

# Get the block count
print(rpc.callrpc("getblockcount"))
```

Arguments are passed as a python objects in a list.

```
from cuatrorpc import RpcClient

rpc = RpcClient(username="username", password="password", port=8033)

block_height = 1337

# Get get block hash from index
block_hash = rpc.callrpc("getblockhash", [block_height])

# Get the block details along with all of the trasnaction data for the block
block_details = rpc.callrpc("getblock", [block_hash, 2])

# Since the return for 'getblock' is a json object,
# block_details is automatically converted to a python object

# Get the timestamp of the block

timestamp = block_details['time']

print(timestamp)
```

For Async operations, use the RpcClientAsync class

```
from cuatrorpc import RpcClientAsync
import asyncio


rpc = RpcClientAsync(username="username", password="password", port=8033)

async def main():
  # Get the block count
  block_count = await rpc.callrpc("getblockcount")
  print(block_count)

if __name__ == "__main__":
  asyncio.run(main())
```

## Usage CLI Binary

You can optionally use the cli binary to make rpc calls.

```
from cuatrorpc import RpcClientCLI


rpc = RpcClientCLI(cli_bin_path="/path/to/bitcoin-cli",
                                data_dir_path="/path/to/.bitcoin",
                                daemon_conf_path="/path/to/.bitcoin/bitcoin.conf"
                                )

# Everything from here is the same as the http version except the method is called callrpc_cli

# Get the block count
print(rpc.callrpc_cli("getblockcount"))
```

```
from cuatrorpc import RpcClientCLI


rpc = RpcClientCLI(cli_bin_path="/path/to/bitcoin-cli",
                                data_dir_path="/path/to/.bitcoin",
                                daemon_conf_path="/path/to/.bitcoin/bitcoin.conf",
                                use_alias=True,
                                )

# You can optionally pass the use_alias=True arg. This allows you to use callrpc as well as callrpc_cli

# Get the block count
print(rpc.callrpc("getblockcount"))
```

For Async operations, use the RpcClientCLIAsync class

```
from cuatrorpc import RpcClientCLIAsync
import asyncio


rpc = RpcClientCLIAsync(cli_bin_path="/path/to/bitcoin-cli",
                                data_dir_path="/path/to/.bitcoin",
                                daemon_conf_path="/path/to/.bitcoin/bitcoin.conf"
                                )

# From here everything is the same as with the async http version.

async def main():
  # Get the block count
  block_count = await rpc.callrpc_cli("getblockcount")
  print(block_count)

if __name__ == "__main__":
  asyncio.run(main())
```
