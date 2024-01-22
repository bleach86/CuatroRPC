from typing import Optional, List, Any, Dict
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from cuatrorpc.cuatrorpc_rs import RpcClient, RpcClientCLI


class RpcClientAsync:
    def __init__(
        self,
        username: str,
        password: str,
        port: int,
        host: Optional[str] = "localhost",
        use_https: Optional[bool] = False,
        timeout: Optional[int] = 120,
        max_workers: Optional[int] = 64,
    ) -> None:
        self.rpc = RpcClient(
            username=username,
            password=password,
            port=port,
            host=host,
            use_https=use_https,
            timeout=timeout,
        )
        self.max_workers = max_workers

        self.async_init = False

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
        if not self.async_init:
            self._init_executor()
        return await self.loop.run_in_executor(
            self.executor, self.rpc.callrpc, method, params, wallet
        )


class RpcClientCLIAsync:
    def __init__(
        self,
        cli_bin: str,
        data_dir: str,
        daemon_conf: str,
        max_workers: int = 64,
    ) -> None:
        self.rpc = RpcClientCLI(
            cli_bin=cli_bin, data_dir=data_dir, daemon_conf=daemon_conf
        )

        self.max_workers: int = max_workers
        self.async_init: bool = False

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
        if not self.async_init:
            self._init_executor()
        return await self.loop.run_in_executor(
            self.executor, self.rpc.callrpc, method, params, wallet
        )
