mod cpu_identity;
mod format;
mod metrics;
mod snapshot;
mod telemetry;
mod transport;

fn main() -> std::io::Result<()> {
    println!("WynCommand // Observatory :3");
    println!();

    transport::run_server()
}
