from typing import List, Any, Optional

class RpcClient:
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
    ) -> Any: ...

class RpcClientCLI:
    def __new__(
        self,
        cli_bin: str,
        data_dir: str,
        daemon_conf: str,
    ): ...
    def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        wallet: Optional[str] = "",
    ) -> Any: ...
