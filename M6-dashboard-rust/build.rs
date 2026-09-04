use std::{
    env,
    path::PathBuf,
    process::Command,
};

fn main() {
    let out_dir = PathBuf::from(
        env::var("OUT_DIR")
            .expect("OUT_DIR missing"),
    );

    let asm = PathBuf::from("../asm/cpuid.asm");
    let object = out_dir.join("cpuid.o");

    let status = Command::new("nasm")
        .arg("-f")
        .arg("elf64")
        .arg(&asm)
        .arg("-o")
        .arg(&object)
        .status()
        .expect("failed to run NASM");

    assert!(
        status.success(),
        "NASM failed"
    );

    let library = out_dir.join("libwynasm.a");

    let status = Command::new("ar")
        .arg("rcs")
        .arg(&library)
        .arg(&object)
        .status()
        .expect("failed to run ar");

    assert!(
        status.success(),
        "ar failed"
    );

    println!(
        "cargo:rustc-link-search=native={}",
        out_dir.display()
    );

    println!(
        "cargo:rustc-link-lib=static=wynasm"
    );

    println!(
        "cargo:rerun-if-changed={}",
        asm.display()
    );
}
