mod format;
mod metrics;
mod snapshot;
mod telemetry;
mod transport;
mod cpu_identity;

fn main() -> std::io::Result<()> {
    println!("WynCommand // Observatory :3");
    println!();

    transport::run_server()
}
