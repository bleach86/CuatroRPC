from typing import List

def callrpc_rs(url: str, method: str, params: str) -> List[int]: ...
def callrpc_cli_rs(
    cli_bin: str,
    data_dir: str,
    daemon_conf: str,
    method: str,
    wallet: str,
    call_args: str,
) -> str: ...
