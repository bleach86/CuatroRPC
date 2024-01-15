from typing import Optional, List, Any

class RpcClientBase:
    def __init__(
        self,
        *,
        host: str = ...,
        username: str = ...,
        password: str = ...,
        use_https: bool = ...,
        port: int = ...,
    ) -> None: ...
    def _callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = ...,
        wallet: Optional[str] = ...,
    ) -> Any: ...

class RpcClient(RpcClientBase):
    def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = ...,
        wallet: Optional[str] = ...,
    ) -> Any: ...

class RpcClientAsync(RpcClientBase):
    def __init__(
        self,
        *,
        host: str = ...,
        username: str = ...,
        password: str = ...,
        use_https: bool = ...,
        port: int = ...,
        max_workers: int = ...,
    ): ...
    def init_executor(self) -> None: ...
    async def callrpc(
        self,
        method: str,
        params: Optional[List[Any]] = ...,
        wallet: Optional[str] = ...,
    ) -> Any: ...

class _RpcClientCLIBase:
    def __init__(
        self, *, cli_bin_path: str, data_dir_path: str, daemon_conf_path: str
    ) -> None: ...
    def _callrpc_cli(
        self,
        method: str,
        params: Optional[List[Any]] = ...,
        wallet: Optional[str] = ...,
    ) -> Any: ...

class RpcClientCLI(_RpcClientCLIBase):
    def __init__(
        self,
        *,
        cli_bin_path: str,
        data_dir_path: str,
        daemon_conf_path: str,
        use_alias: bool = ...,
    ) -> None: ...
    def callrpc_cli(
        self,
        method: str,
        params: Optional[List[Any]] = ...,
        wallet: Optional[str] = ...,
    ) -> Any: ...

class RpcClientCLIAsync(_RpcClientCLIBase):
    def __init__(
        self,
        *,
        cli_bin_path: str,
        data_dir_path: str,
        daemon_conf_path: str,
        use_alias: bool = ...,
        max_workers: int = ...,
    ) -> None: ...
    def _init_executor(self) -> None: ...
    async def callrpc_cli(
        self,
        method: str,
        params: Optional[List[Any]] = ...,
        wallet: Optional[str] = ...,
    ) -> Any: ...
