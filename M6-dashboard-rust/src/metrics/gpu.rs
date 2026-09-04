use nvml_wrapper::Nvml;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuSnapshot {
    pub available: bool,

    pub model: String,

    pub utilization_percent: f32,
    pub memory_utilization_percent: f32,

    pub vram_total_bytes: u64,
    pub vram_used_bytes: u64,

    pub temperature_c: f32,
    pub power_watts: f32,

    pub pcie_rx_mib_s: f32,
    pub pcie_tx_mib_s: f32,
}

pub struct GpuCollector {
    nvml: Option<Nvml>,
}

impl GpuCollector {
    pub fn new() -> Self {
        Self {
            nvml: Nvml::init().ok(),
        }
    }
}

impl Default for GpuCollector {
    fn default() -> Self {
        Self::new()
    }
}
