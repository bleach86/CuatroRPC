use pyo3::prelude::*;
use serde_json::Value;
use std::io::Read;
use std::process::Command;

#[pyfunction]
fn callrpc_rs(url: &str, method: &str, params: &str) -> PyResult<Option<Vec<u8>>> {
    let request_body: String = format!(
        r#"
        {{
            "jsonrpc": "2.0",
            "id": "2",
            "method": "{}",
            "params": {}
        }}
    "#,
        method, params
    );

    let response: ureq::Response = ureq::post(url)
        .set("Content-Type", "application/json")
        .set("User-Agent", "CuatroRPC")
        .send_string(&request_body)
        .map_err(|e: ureq::Error| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC ERROR: {}", e))
        })?;

    let len_content: usize = response.header("Content-Length").unwrap().parse()?;

    let mut response_bytes: Vec<u8> = Vec::with_capacity(len_content);
    response
        .into_reader()
        .take((len_content + 1) as u64)
        .read_to_end(&mut response_bytes)
        .map_err(|e: std::io::Error| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Read Error: {}", e))
        })?;

    Ok(Some(response_bytes))
}

#[pyfunction]
fn callrpc_cli_rs(
    cli_bin: &str,
    data_dir: &str,
    daemon_conf: &str,
    method: &str,
    wallet: &str,
    call_args: &str,
) -> PyResult<String> {
    let parsed_json: Value = serde_json::from_str(call_args).expect("Failed to parse JSON");

    let formatted_args: Vec<String> = parsed_json
        .as_array()
        .expect("Expected JSON array")
        .iter()
        .map(|element: &Value| {
            if let Some(string_value) = element.as_str() {
                if _is_numeric(string_value) || _is_probably_json(string_value) {
                    string_value.to_string()
                } else {
                    let unquoted_string: &str = _unquote_sting(string_value);
                    unquoted_string.to_string()
                }
            } else {
                element.to_string()
            }
        })
        .collect();
    let mut command: Command = Command::new(cli_bin);
    command.arg(format!("-datadir={}", data_dir));
    command.arg(format!("-conf={}", daemon_conf));

    if !wallet.is_empty() {
        command.arg(format!("-rpcwallet={}", wallet));
    }

    command.arg(method);
    command.args(formatted_args);

    let output: Result<std::process::Output, std::io::Error> = command.output();

    match output {
        Ok(result) => {
            if result.status.success() {
                let result_str: std::borrow::Cow<'_, str> = String::from_utf8_lossy(&result.stdout);
                let res: String = result_str.replace("\n", "");
                if _is_numeric(res.clone()) || _is_probably_json(res.clone()) {
                    Ok(format!("{{\"result\": {}, \"error\": 0}}", res))
                } else {
                    Ok(format!("{{\"result\": \"{}\", \"error\": 0}}", res))
                }
            } else {
                let error_message: std::borrow::Cow<'_, str> =
                    String::from_utf8_lossy(&result.stderr);
                let err_res: String = error_message.replace("\n", "");
                Ok(format!("{{\"result\": 0, \"error\": \"{}\"}}", err_res))
            }
        }
        Err(e) => Ok(format!("{{\"result\": 0, \"error\": \"{}\"}}", e)),
    }
}

fn _is_numeric<S: AsRef<str>>(input: S) -> bool {
    for char in input.as_ref().chars() {
        if !matches!(char, '0'..='9' | '.') {
            return false;
        }
    }
    true
}

fn _is_probably_json<S: AsRef<str>>(input: S) -> bool {
    let input_str: &str = input.as_ref();

    input_str.starts_with("{") && input_str.ends_with("}")
        || input_str.starts_with("[") && input_str.ends_with("]")
}

fn _unquote_sting<'a, S: AsRef<str> + ?Sized>(input: &'a S) -> &'a str {
    let input_str: &str = input.as_ref();

    let quotes: Vec<&str> = vec!["'", "\"", "'''", "\"\"\""];

    for quote in quotes {
        if input_str.starts_with(quote) && input_str.ends_with(quote) {
            let start: usize = quote.len();
            let end: usize = input_str.len() - quote.len();
            return &input_str[start..end];
        }
    }

    input_str
}

#[pymodule]
fn cuatrorpc_rs(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(callrpc_rs, m)?)?;
    m.add_function(wrap_pyfunction!(callrpc_cli_rs, m)?)?;
    Ok(())
}
