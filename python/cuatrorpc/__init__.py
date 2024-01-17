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


from typing import Optional, List, Any, Dict
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from cuatrorpc import cuatrorpc_rs


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
        wallet: str = "",
    ) -> Any:
        """Private method for making RPC calls
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """

        response: Dict[str, Any] = cuatrorpc_rs.callrpc_rs(
            self.url,
            method,
            wallet,
            params if params is not None else [],
        )


        if response["error"]:
            raise ValueError("RPC error " + str(response["error"]))

        return response["result"]


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
        wallet: str = "",
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
    ) -> None:
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
        wallet: str = "",
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


class _RpcClientCLIBase:
    def __init__(
        self, *, cli_bin_path: str, data_dir_path: str, daemon_conf_path: str
    ) -> None:
        self.cli_bin = cli_bin_path
        self.data_dir = data_dir_path
        self.daemon_conf = daemon_conf_path

    def _callrpc_cli(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: str = "",
    ) -> Any:
        """Private method for making RPC calls via CLI binary
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """

        response: Dict[str, Any] = cuatrorpc_rs.callrpc_cli_rs(
            self.cli_bin,
            self.data_dir,
            self.daemon_conf,
            method,
            wallet,
            params if params is not None else [],
        )

        if response["error"]:
            raise ValueError("RPC error " + str(response["error"]))

        return response["result"]


class RpcClientCLI(_RpcClientCLIBase):
    """Main sync CLI Rpc Client class

    Keyword arguments:
    cli_bin_path -- str: The full path to the CLI binary e.g. /home/user/btc_bin/bitcoin-cli
    data_dir_path -- str: The full path to the daemon data directory e.g. /home/user/.bitcoin
    daemon_conf -- str: The full path to the daemon configuration file. e.g bitcoin.conf
    use_alias -- bool: Set to True to use callrpc for calls to callrpc_cli.
    """

    def __init__(
        self,
        *,
        cli_bin_path: str,
        data_dir_path: str,
        daemon_conf_path: str,
        use_alias: bool = False,
    ) -> None:
        super().__init__(
            cli_bin_path=cli_bin_path,
            data_dir_path=data_dir_path,
            daemon_conf_path=daemon_conf_path,
        )

        if use_alias:
            self.callrpc = self.callrpc_cli

    def callrpc_cli(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: str = "",
    ) -> Any:
        """Method for making RPC calls via CLI binary
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """

        return self._callrpc_cli(method=method, params=params, wallet=wallet)


class RpcClientCLIAsync(_RpcClientCLIBase):
    """Async CLI Rpc Client class

    Keyword arguments:
    cli_bin_path -- str: The full path to the CLI binary e.g. /home/user/btc_bin/bitcoin-cli
    data_dir_path -- str: The full path to the daemon data directory e.g. /home/user/.bitcoin
    daemon_conf -- str: The full path to the daemon configuration file. e.g bitcoin.conf
    use_alias -- bool: Set to True to use callrpc for calls to callrpc_cli.
    max_workers -- int: The maximum number of threadpool workers to spawn.
    """

    def __init__(
        self,
        *,
        cli_bin_path: str,
        data_dir_path: str,
        daemon_conf_path: str,
        use_alias: bool = False,
        max_workers: int = 64,
    ) -> None:
        super().__init__(
            cli_bin_path=cli_bin_path,
            data_dir_path=data_dir_path,
            daemon_conf_path=daemon_conf_path,
        )

        self.max_workers: int = max_workers
        self.async_init: bool = False

        if use_alias:
            self.callrpc = self.callrpc_cli

    def _init_executor(self) -> None:
        self.loop: AbstractEventLoop = asyncio.get_running_loop()

        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=self.max_workers,
        )
        self.async_init = True

    async def callrpc_cli(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: str = "",
    ) -> Any:
        """Async wrapper method for making RPC calls via CLI binary
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
            self.executor, self._callrpc_cli, method, params, wallet
        )


if __name__ == "__main__":
    pass
