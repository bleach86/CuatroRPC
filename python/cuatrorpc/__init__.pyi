"""CuatroRPC

Included classes:
- RpcClient: Rpc client class
- RpcClientAsync: ASync Rpc client class
- RpcClientCLI: Class for making RPC calls via the bitcoin-cli binary 
- RpcClientCLIAsync: Async Class for making RPC calls via the bitcoin-cli binary

Usage:
from cuatrorpc import RpcClient

rpc = RpcClient(username="user", password="password", port=8333)

print(rpc.callrpc("getblockcount"))

"""

from typing import Optional, List, Any

class RpcClient:
    """Main sync Rpc Client class

    Keyword arguments:
    host -- str: The hostname or ip of the RPC server. Default 'localhost'
    username -- str: username for the client session.
    password -- str: password for the client session.
    use_https -- bool: Sets wether to use https or http. Default False
    port -- int: The port used to connect to the RPC server.
    """

    def __new__(
        self,
        username: str,
        password: str,
        port: int,
        host: Optional[str] = "localhost",
        use_https: Optional[bool] = False,
        timeout: Optional[int] = 120,
    ): ...
    def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: Optional[str] = "",
    ) -> Any:
        """Method for making RPC calls
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """
        ...

class RpcClientCLI:
    """Main sync CLI Rpc Client class

    Keyword arguments:
    cli_bin -- str: The full path to the CLI binary e.g. /home/user/btc_bin/bitcoin-cli
    data_dir -- str: The full path to the daemon data directory e.g. /home/user/.bitcoin
    daemon_conf -- str: The full path to the daemon configuration file. e.g bitcoin.conf
    """

    def __new__(
        self,
        cli_bin: str,
        data_dir: str,
        daemon_conf: str,
    ): ...
    def callrpc(
        self,
        method: str,
        call_args: Optional[List[Any]] = None,
        wallet: Optional[str] = "",
    ) -> Any:
        """Method for making RPC calls via CLI binary
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """
        ...

class RpcClientAsync:
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
        username: str,
        password: str,
        port: int,
        host: Optional[str] = "localhost",
        use_https: Optional[bool] = False,
        timeout: Optional[int] = 120,
    ): ...
    def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: Optional[str] = "",
    ) -> Any:
        """Async wrapper method for making RPC calls
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """

        ...

class RpcClientCLIAsync:
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
        cli_bin: str,
        data_dir: str,
        daemon_conf: str,
    ): ...
    def callrpc(
        self,
        method: str,
        call_args: Optional[List[Any]] = None,
        wallet: Optional[str] = "",
    ) -> Any:
        """Async wrapper method for making RPC calls via CLI binary
        Arguments:
        method -- str: The RPC method to call. Example "getblockcount"

        Keyword arguments:
        params -- List[Any]: A list of paramaters to pass along with the method.
        wallet -- Optional[str]: Optionally specify the wallet to make the call with.
        Returns -- Any: Returns the response from the RPC server.
        """
        ...
