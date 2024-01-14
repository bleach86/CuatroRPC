use pyo3::prelude::*;
use std::io::Read;

#[pyfunction]
fn callrpc(url: &str, method: &str, params: &str) -> PyResult<Option<Vec<u8>>> {
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

#[pymodule]
fn cuatrorpc_rs(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(callrpc, m)?)?;
    Ok(())
}
