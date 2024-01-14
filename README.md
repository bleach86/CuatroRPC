# CuatroRPC
Fast Bitcoin RPC Client Library for Python leveraging Rust.

CuatroRPC aims to be a simple and fast RPC Client for Bitcoin compatble RPC servers.

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

# Since the retrun for 'getblock' is a json object,
# block_details is automatically converted to a python object

# Get the timestamp of the block

timestamp = block_details['time']

print(timestamp)
```

For Async oporations, use the RpcClientAsync class

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
