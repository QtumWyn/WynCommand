use crate::metrics::{
    cpu::CpuSnapshot,
    memory::MemorySnapshot,
    scheduler::SchedulerSnapshot,
    npu::NpuSnapshot,
};
use serde::{Serialize, Deserialize};


#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemSnapshot {
    pub schema_version: u16,
    pub captured_at_unix_ms: u64,
    pub cpu: CpuSnapshot,
    pub memory: MemorySnapshot,
    pub npu: NpuSnapshot,
    pub scheduler: SchedulerSnapshot,
}
