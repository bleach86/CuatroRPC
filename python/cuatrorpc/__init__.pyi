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
