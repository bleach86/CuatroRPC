"""CuatroRPC

Included classes:
- RpcClient: Rpc client class
- RpcClientAsync: ASync Rpc client class
- RpcClientPortOnCall: Rpc client class talkig port on call
- RpcClientPortOnCallAsync: Async Rpc client class talkig port on call

Usage:
from cuatrorpc import RpcClient

rpc = RpcClient(host="localhost", username="user", password="password")

print(rpc.callrpc("getblockcount"))

"""


from typing import Optional, List, Any, Dict
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from cuatrorpc import cuatrorpc_rs
import orjson


class _RpcClientBase:
    """Base class for RPC client classes

    Keyword arguments:
    host -- str: The hostname or ip of the RPC server. Default 'localhost'
    username -- str: username for the client session.
    password -- str: password for the client session.
    use_https -- bool: Sets wether to use https or http. Default False
    port -- int: The port used to connect to the RPC server.
    """

    def __init__(
        self,
        *,
        host: str = "localhost",
        username: str = "",
        password: str = "",
        use_https: bool = False,
        port: int = 0,
    ) -> None:
        if not username:
            raise ValueError("Missing required username.")
        if not password:
            raise ValueError("Missing required password.")
        if not port:
            raise ValueError("Missing required port.")

        if use_https:
            self.scheme = "https"
        else:
            self.scheme = "http"

        self.url = f"{self.scheme}://{username}:{password}@{host}:{port}"

    def _callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: Optional[str] = None,
    ) -> Any:
        """Private method for making RPC calls
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """
        if wallet:
            url: str = f"{self.url}/wallet/{wallet}"
        else:
            url = self.url

        if params is None:
            params_str: str = "[]"
        else:
            params_str = orjson.dumps(params).decode()
        response: List[int] = cuatrorpc_rs.callrpc(
            url,
            method,
            params_str,
        )
        resp_decoded: Dict[str, Any] = orjson.loads(bytes(response))

        if resp_decoded["error"]:
            raise ValueError("RPC error " + str(resp_decoded["error"]))

        return resp_decoded["result"]


class RpcClient(_RpcClientBase):
    """Main sync Rpc Client class

    Keyword arguments:
    host -- str: The hostname or ip of the RPC server. Default 'localhost'
    username -- str: username for the client session.
    password -- str: password for the client session.
    use_https -- bool: Sets wether to use https or http. Default False
    port -- int: The port used to connect to the RPC server.
    """

    def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: Optional[str] = None,
    ) -> Any:
        """Method for making RPC calls
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """

        return self._callrpc(method=method, params=params, wallet=wallet)


class RpcClientAsync(_RpcClientBase):
    """Async Rpc Client class

    Keyword arguments:
    host -- str: The hostname or ip of the RPC server. Default 'localhost'
    username -- str: username for the client session.
    password -- str: password for the client session.
    use_https -- bool: Sets wether to use https or http. Default False
    port -- int: The port used to connect to the RPC server.
    max_workers -- int: The maximum number of threadpool workers to spawn.
    """

    def __init__(
        self,
        *,
        host: str = "localhost",
        username: str = "",
        password: str = "",
        use_https: bool = False,
        port: int = 0,
        max_workers: int = 64,
    ):
        super().__init__(
            host=host,
            username=username,
            password=password,
            use_https=use_https,
            port=port,
        )

        self.max_workers: int = max_workers
        self.async_init: bool = False

    def _init_executor(self) -> None:
        self.loop: AbstractEventLoop = asyncio.get_running_loop()

        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=self.max_workers,
        )
        self.async_init = True

    async def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: Optional[str] = None,
    ) -> Any:
        """Async wrapper method for making RPC calls
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """
        if not self.async_init:
            self._init_executor()
        return await self.loop.run_in_executor(
            self.executor, self._callrpc, method, params, wallet
        )


if __name__ == "__main__":
    pass
