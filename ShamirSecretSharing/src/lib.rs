use pyo3::prelude::*;
use sss::field::Field;
use sss::gf2n::{GF256};
use sss::shamir::{CompactShamir, Shamir};
use regex::Regex;
use std::fmt::{Debug, Display};
use std::fs::File;
use std::io::{BufRead, BufReader, Read, Write};

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn split_private_key(filename: &str, k: usize, n: usize) {
    // shares should be in the range of [1, 255]
    //let shares = 10;
    // threshold should be in the range of [1, shares]
    //let threshold = 3;
    // split
    let secret_file = "privateKey.txt";
    split::<GF256, CompactShamir>(filename, k, n);
}

#[pyfunction]
fn reconstruct_private_key(filename: &str, k: usize) -> PyResult<String> {
    // reconstruct
    let private_key = reconstruct::<GF256, CompactShamir>(filename, k);
    Ok(private_key)
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn ShamirSecretSharing(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(split_private_key, m)?)?;
    m.add_function(wrap_pyfunction!(reconstruct_private_key, m)?)?;
    Ok(())
}

fn split<F: Field + Debug + Display, S: Shamir<F>>(filename: &str, k: usize, n: usize)
where
    S::Share: Display,
{
    let secret = parse_secret::<F>(filename);
    //println!("Secret = {}", secret);

    let shares = S::split(&secret, k, n);
    println!("Shares:");
    let mut index = 0;
    for s in &shares {
        //println!("{}", s);
        let mut owned_string: String = "./keys/partial_key_".to_owned();
        owned_string.push_str(&index.to_string().to_owned());
        let borrowed_string: &str = ".txt";
        owned_string.push_str(borrowed_string);
    
        //println!("{}", owned_string);
        let mut file = std::fs::File::create(owned_string).expect("create failed");
        file.write_all(s.to_string().as_bytes()).expect("write failed");
        //println!("data written to file" );
        index = index + 1;
    }
}



fn reconstruct<F: Field + Debug + Display, S: Shamir<F>>(filename: &str, k: usize) -> String
where
    S::Share: Display,
{
    let shares = parse_shares::<F, S>(filename);
    /*
    println!("Shares:");
    for s in &shares {
        println!("{}", s);
    }
    */

    assert!(
        shares.len() >= k,
        "Found fewer shares than the threshold, cannot reconstruct!"
    );

    let secret = S::reconstruct(&shares, k);
    
    let mut secretStr = String::from("hello world");
    
    match secret {
        Some(s) => secretStr = s.to_string(),
        None => println!("Could not reconstruct the secret..."),
    }
    
    //println!("Private Key: {}", secretStr);
    secretStr
}

// read the secret from a file for split
fn parse_secret<F: Field>(filename: &str) -> F {
    let mut file = File::open(filename).unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    let regex = Regex::new(r"^([0-9a-fA-F]+)\n?$").unwrap();
    let captures = match regex.captures(&contents) {
        Some(cap) => cap,
        None => panic!("Secret file must contains hexadecimal characters only",),
    };
    let bytes = match hex::decode(&captures[1]) {
        Ok(bytes) => bytes,
        Err(e) => panic!(
            "Couldn't parse secret file as hexadecimal characters: {}",
            e
        ),
    };
    match F::from_bytes(bytes.as_slice()) {
        Some(f) => f,
        None => panic!("Secret is not a valid represetation of a field element"),
    }
}

// read shares from a file for reconstruct
fn parse_shares<F: Field + Debug + Display, S: Shamir<F>>(filename: &str) -> Vec<S::Share> {
    let file = File::open(filename).unwrap();
    BufReader::new(file)
        .lines()
        .map(|line| S::parse_share(&line.unwrap()).unwrap())
        .collect()
}