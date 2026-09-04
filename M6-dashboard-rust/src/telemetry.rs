use std::{
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

use sysinfo::{CpuRefreshKind, System};

use crate::{
    metrics::{
        cpu::collect_cpu,
        memory::MemoryCollector,
        npu::NpuCollector,
        scheduler::SchedulerCollector,
    },
    snapshot::SystemSnapshot,
    cpu_identity::{read_cpu_identity, CpuIdentity},
};

fn unix_timestamp_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

pub struct TelemetryCollector {
    system: System,
    cpu_identity: CpuIdentity,
    memory: MemoryCollector,
    npu: NpuCollector,
    scheduler: SchedulerCollector,
}

impl TelemetryCollector {
    pub fn new() -> Self {
        let cpu_identity = read_cpu_identity();
        let memory = MemoryCollector::new();
        let npu = NpuCollector::new();
        let scheduler = SchedulerCollector::new();

        let mut system = System::new();

        // Build the CPU list and take the first CPU sample.
        //
        // sysinfo calculates CPU usage from the difference between two samples,
        // so the first reading is not yet useful by itself.
        system.refresh_cpu_list(CpuRefreshKind::everything());
        system.refresh_cpu_all();
        system.refresh_memory();

        // One short startup delay gives us a meaningful second CPU sample.
        //
        // Later, once Observatory has a continuously running event loop, we can
        // remove this startup sleep and simply let the next scheduled refresh
        // become the second sample.
        thread::sleep(Duration::from_millis(250));

        system.refresh_cpu_all();

        Self {
            system,
            cpu_identity,
            memory,
            npu,
            scheduler,
        }
    }

    pub fn sample(&mut self) -> SystemSnapshot {
        self.system.refresh_cpu_all();
        self.system.refresh_memory();
        let scheduler =
            self.scheduler.sample();

        SystemSnapshot {
            schema_version: 1,
            captured_at_unix_ms:
            unix_timestamp_ms(),

            cpu: collect_cpu(
                &self.system,
                &self.cpu_identity,
            ),

            memory:
            self.memory.sample(
                &self.system,
            ),

            npu:
            self.npu.sample(),

            scheduler,
        }
    }
}

impl Default for TelemetryCollector {
    fn default() -> Self {
        Self::new()
    }
}
