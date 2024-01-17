use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList};
use serde_json::Value;
use std::process::Command;

#[pyfunction]
fn callrpc_rs(
    py: Python<'_>,
    url: &str,
    method: &str,
    wallet: &str,
    params: &PyList,
) -> PyResult<Option<PyObject>> {
    let params_str: String = params.to_string();

    let params_sanatized: String = params_str
        .replace("'", "\"")
        .replace("True", "true")
        .replace("False", "false")
        .replace("None", "null");

    let request_body: String = format!(
        r#"
        {{
            "jsonrpc": "2.0",
            "id": "2",
            "method": "{}",
            "params": {}
        }}
    "#,
        method, params_sanatized
    );

    let req_url: String = if wallet.is_empty() {
        url.to_string()
    } else {
        format!("{}/wallet/{}", url, wallet)
    };

    let response: ureq::Response = ureq::post(&req_url)
        .set("Content-Type", "application/json")
        .set("User-Agent", "CuatroRPC")
        .send_string(&request_body)
        .map_err(|e: ureq::Error| PyErr::new::<PyRuntimeError, _>(format!("RPC ERROR: {}", e)))?;

    let resp_json: Value = response.into_json().map_err(|e: std::io::Error| {
        PyErr::new::<PyRuntimeError, _>(format!("JSON Parsing Error: {}", e))
    })?;

    let result_value: Value = resp_json["result"].clone();
    let error_value: i64 = resp_json["error"].as_i64().unwrap_or(0);

    let py_dict: &PyDict = PyDict::new(py);

    if let Some(py_result) = _response_to_py_object(py, &result_value) {
        py_dict.set_item("result", py_result)?;
    } else {
        py_dict.set_item("result", result_value.to_string())?;
    }

    py_dict.set_item("error", error_value)?;
    Ok(Some(py_dict.into_py(py)))
}

#[pyfunction]
fn callrpc_cli_rs(
    py: Python<'_>,
    cli_bin: &str,
    data_dir: &str,
    daemon_conf: &str,
    method: &str,
    wallet: &str,
    call_args: &PyList,
) -> PyResult<PyObject> {
    let call_args_str: String = call_args.to_string();

    let args_sanatized: String = call_args_str
        .replace("'", "\"")
        .replace("True", "true")
        .replace("False", "false")
        .replace("None", "null");

    let parsed_json: Value = serde_json::from_str(&args_sanatized).expect("Failed to parse JSON");

    let formatted_args: Vec<String> = parsed_json
        .as_array()
        .expect("Expected JSON array")
        .iter()
        .map(|element: &Value| {
            if let Some(string_value) = element.as_str() {
                if _is_numeric(string_value) || _is_probably_json(string_value) {
                    string_value.to_string()
                } else {
                    let unquoted_string: &str = _unquote_string(string_value);
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
                let dict: &PyDict = PyDict::new(py);
                if _is_numeric(res.as_str()) {
                    if !res.contains(".") {
                        let py_long: i64 = res.parse()?;
                        dict.set_item("result", py_long)?;
                    } else {
                        let py_float: f64 = res.parse()?;
                        dict.set_item("result", py_float)?;
                    }
                } else {
                    if let Ok(json_value) = serde_json::from_str::<Value>(&res) {
                        dict.set_item("result", _response_to_py_object(py, &json_value))?;
                    } else {
                        dict.set_item("result", res)?;
                    }
                }
                dict.set_item("error", 0)?;
                Ok(dict.into())
            } else {
                let error_message: std::borrow::Cow<'_, str> =
                    String::from_utf8_lossy(&result.stderr);
                let err_res: String = error_message.replace("\n", "");
                let dict: &PyDict = PyDict::new(py);
                dict.set_item("result", 0)?;
                dict.set_item("error", err_res)?;
                Ok(dict.into())
            }
        }
        Err(e) => {
            let dict: &PyDict = PyDict::new(py);
            dict.set_item("result", 0)?;
            dict.set_item("error", e.to_string())?;
            Ok(dict.into())
        }
    }
}

fn _response_to_py_object(py: Python<'_>, value: &Value) -> Option<PyObject> {
    match value {
        Value::Null => None,
        Value::Bool(b) => Some(b.clone().into_py(py)),
        Value::Number(num) => {
            if num.is_i64() {
                Some(num.as_i64().unwrap().into_py(py))
            } else if num.is_f64() {
                Some(num.as_f64().unwrap().into_py(py))
            } else {
                None
            }
        }
        Value::String(s) => Some(s.clone().into_py(py)),
        Value::Array(arr) => {
            let py_list: Vec<Py<PyAny>> = arr
                .iter()
                .map(|v: &Value| _response_to_py_object(py, v))
                .collect::<Option<Vec<PyObject>>>()?;
            Some(py_list.into_py(py))
        }
        Value::Object(obj) => {
            let py_dict: &PyDict = PyDict::new(py);
            for (k, v) in obj {
                if let Some(py_value) = _response_to_py_object(py, v) {
                    py_dict.set_item(k, py_value).ok()?;
                }
            }
            Some(py_dict.into())
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

fn _is_probably_json<S: AsRef<str>>(input: S) -> bool {
    let input_str: &str = input.as_ref();

    input_str.starts_with("{") && input_str.ends_with("}")
        || input_str.starts_with("[") && input_str.ends_with("]")
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
    m.add_function(wrap_pyfunction!(callrpc_rs, m)?)?;
    m.add_function(wrap_pyfunction!(callrpc_cli_rs, m)?)?;
    Ok(())
}
