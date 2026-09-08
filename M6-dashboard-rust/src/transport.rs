use std::{
    io::{self, Write},
    net::{TcpListener, TcpStream},
    thread,
    time::Duration,
};

use crate::{protocol, telemetry::TelemetryCollector};

const LISTEN_ADDRESS: &str = "127.0.0.1:4767";
const SAMPLE_INTERVAL: Duration = Duration::from_millis(500);

pub fn run_server() -> io::Result<()> {
    let listener = TcpListener::bind(LISTEN_ADDRESS)?;

    println!("Telemetry server listening on {LISTEN_ADDRESS}");

    let mut telemetry = TelemetryCollector::new();

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                println!("Observatory client connected");

                if let Err(error) = stream_snapshots(stream, &mut telemetry) {
                    eprintln!("Observatory client disconnected: {error}");
                }
            }

            Err(error) => {
                eprintln!("Failed to accept Observatory connection: {error}");
            }
        }
    }

    Ok(())
}

fn stream_snapshots(mut stream: TcpStream, telemetry: &mut TelemetryCollector) -> io::Result<()> {
    loop {
        let snapshot = telemetry.sample();

        let wire_snapshot = protocol::to_wire(&snapshot);

        let json = serde_json::to_string(&wire_snapshot).map_err(io::Error::other)?;

        writeln!(stream, "{json}")?;

        stream.flush()?;

        thread::sleep(SAMPLE_INTERVAL);
    }
}
