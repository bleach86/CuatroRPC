from typing import List, Dict, Any

def callrpc_rs(url: str, method: str, wallet:str, params: List[Any]) -> Dict[str, Any]: ...
def callrpc_cli_rs(
    cli_bin: str,
    data_dir: str,
    daemon_conf: str,
    method: str,
    wallet: str,
    call_args: List[Any],
) -> Dict[str, Any]: ...
