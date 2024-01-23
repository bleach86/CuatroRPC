use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyList;
use serde_json::Value;
use std::process::Command;
use std::time::Duration;
use std::vec;
use ureq::{Agent, AgentBuilder};

use pythonize::{depythonize, pythonize};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Post<'r> {
    jsonrpc: &'r str,
    id: &'r str,
    method: &'r str,
    params: Value,
}

#[pyclass]
struct RpcClient {
    url: String,
    rpc_timeout: u64,
}
#[pymethods]
impl RpcClient {
    #[new]
    #[pyo3(
        text_signature = "(username: str, password: str, port: int, host: str = \"localhost\", use_https: bool = False, timeout: int = 120)"
    )]
    fn new(
        username: String,
        password: String,
        port: u16,
        host: Option<String>,
        use_https: Option<bool>,
        timeout: Option<u64>,
    ) -> Self {
        let rpc_host: String = host.unwrap_or("localhost".to_string());
        let _use_secure: bool = use_https.unwrap_or(false);

        let scheme: String = if _use_secure {
            "https://".to_string()
        } else {
            "http://".to_string()
        };

        let url: String = format!("{}{}:{}@{}:{}", scheme, username, password, rpc_host, port);
        let rpc_timeout: u64 = timeout.unwrap_or(120);

        RpcClient { url, rpc_timeout }
    }

    fn callrpc(
        &self,
        py: Python<'_>,
        method: &str,
        params: Option<&PyList>,
        wallet: Option<&str>,
    ) -> PyResult<Option<PyObject>> {
        let agent: Agent = AgentBuilder::new()
            .timeout_read(Duration::from_secs(self.rpc_timeout))
            .timeout(Duration::from_secs(self.rpc_timeout))
            .build();

        let params_value: Vec<Value> =
            depythonize(params.unwrap_or(PyList::empty(py)).as_ref()).unwrap();

        let post: Post<'_> = Post {
            jsonrpc: "1.0",
            id: "2",
            method,
            params: Value::Array(params_value),
        };

        let request_url: String = if let Some(wallet_opt) = wallet {
            format!("{}/wallet/{}", self.url, wallet_opt)
        } else {
            self.url.clone()
        };

        let response: ureq::Response = agent
            .post(&request_url)
            .set("Content-Type", "application/json")
            .send_json(&post)
            .map_err(|e: ureq::Error| {
                PyErr::new::<PyRuntimeError, _>(format!("RPC ERROR: {}", e))
            })?;

        let resp_json: Value = response.into_json().map_err(|e: std::io::Error| {
            PyErr::new::<PyRuntimeError, _>(format!("JSON Parsing Error: {}", e))
        })?;

        let resp_result: Value = resp_json["result"].clone();
        let resp_error: Value = resp_json["error"].clone();

        match resp_error {
            Value::Null => Ok(Some(pythonize(py, &resp_result).unwrap())),
            _ => Err(PyErr::new::<PyRuntimeError, _>(format!("{}", resp_error))),
        }
    }
}

#[pyclass]
struct RpcClientCLI {
    dir_args: Vec<String>,
    cli_bin_path: String,
}

#[pymethods]
impl RpcClientCLI {
    #[new]
    #[pyo3(text_signature = "(cli_bin: str, data_dir: str, daemon_conf: str)")]
    fn new(cli_bin: String, data_dir: String, daemon_conf: String) -> Self {
        let dir_args: Vec<String> = vec![
            format!("-datadir={}", &data_dir),
            format!("-conf={}", &daemon_conf),
        ];

        let cli_bin_path: String = cli_bin;

        RpcClientCLI {
            dir_args,
            cli_bin_path,
        }
    }

    fn callrpc(
        &self,
        py: Python<'_>,
        method: &str,
        params: Option<&PyList>,
        wallet: Option<&str>,
    ) -> PyResult<PyObject> {
        let parsed_json: Vec<Value> =
            depythonize(params.unwrap_or(PyList::empty(py)).as_ref()).unwrap();

        let formatted_args: Vec<String> = parsed_json
            .iter()
            .map(|element: &Value| {
                if let Some(string_value) = element.as_str() {
                    match element {
                        Value::Number(_) | Value::Object(_) | Value::Array(_) => {
                            string_value.to_string()
                        }
                        _ => {
                            let unquoted_string: &str = _unquote_string(string_value);
                            unquoted_string.to_string()
                        }
                    }
                } else {
                    element.to_string()
                }
            })
            .collect();

        let mut command: Command = Command::new(&self.cli_bin_path);

        command.args(&self.dir_args);

        if let Some(wallet_opt) = wallet {
            command.arg(format!("-rpcwallet={}", wallet_opt));
        }

        command.arg(method);
        command.args(formatted_args);

        let output: Result<std::process::Output, std::io::Error> = command.output();

        match output {
            Ok(result) => {
                if result.status.success() {
                    let result_str: std::borrow::Cow<'_, str> =
                        String::from_utf8_lossy(&result.stdout);
                    let res: String = result_str.replace("\n", "");

                    if _is_numeric(res.as_str()) {
                        if !res.contains(".") {
                            let py_long: i64 = res.parse()?;
                            return Ok(pythonize(py, &py_long).unwrap());
                        } else {
                            let py_float: f64 = res.parse()?;
                            return Ok(pythonize(py, &py_float).unwrap());
                        }
                    } else {
                        if let Ok(json_value) = serde_json::from_str::<Value>(&res) {
                            return Ok(pythonize(py, &json_value).unwrap());
                        }
                    }
                    Ok(pythonize(py, &res).unwrap())
                } else {
                    let error_message: std::borrow::Cow<'_, str> =
                        String::from_utf8_lossy(&result.stderr);
                    Err(PyErr::new::<PyRuntimeError, _>(format!(
                        "{}",
                        error_message
                    )))
                }
            }
            Err(e) => Err(PyErr::new::<PyRuntimeError, _>(format!(
                "{}",
                e.to_string()
            ))),
        }
    }
}

fn _is_numeric(input: &str) -> bool {
    for char in input.chars() {
        if !matches!(char, '0'..='9' | '.') {
            return false;
        }
    }
    true
}

fn _unquote_string<'a, S: AsRef<str> + ?Sized>(input: &'a S) -> &'a str {
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
    m.add_class::<RpcClient>()?;
    m.add_class::<RpcClientCLI>()?;
    Ok(())
}
