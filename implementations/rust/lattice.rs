use std::collections::HashSet;

const PROFILE_ID: &str = "qsol-3x3x3-sierpinski-derived-memory/1";
const LEXICOGRAPHIC_TRAVERSAL: &str = "qsol.lexicographic-27/1";
const PHI_STRIDE_TRAVERSAL: &str = "qsol.phi-stride-27/1";
const PHI_STRIDE: usize = 17;
const TOP_LEVEL_CELL_COUNT: usize = 27;
const MAX_RECURSIVE_DEPTH: usize = 8;
const MAX_ADDRESS_LENGTH: usize = 71;
const CONFORMANCE_PROTOCOL: &str = "qsol-lattice-conformance/1";
const EXPECTED_FINGERPRINT: &str =
    "sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf";

fn lexicographic_cells() -> Vec<String> {
    let mut cells = Vec::with_capacity(TOP_LEVEL_CELL_COUNT);
    for x in 0..3 {
        for y in 0..3 {
            for z in 0..3 {
                cells.push(format!("L[{x},{y},{z}]"));
            }
        }
    }
    assert_eq!(cells.len(), TOP_LEVEL_CELL_COUNT);
    assert_eq!(cells.iter().collect::<HashSet<_>>().len(), TOP_LEVEL_CELL_COUNT);
    cells
}

fn phi_stride_cells() -> Vec<String> {
    let cells = lexicographic_cells();
    let order: Vec<String> = (0..TOP_LEVEL_CELL_COUNT)
        .map(|step| cells[(step * PHI_STRIDE) % TOP_LEVEL_CELL_COUNT].clone())
        .collect();
    assert_eq!(order.iter().collect::<HashSet<_>>().len(), TOP_LEVEL_CELL_COUNT);
    order
}

fn parse_segment(segment: &str) -> Result<(u8, u8, u8), &'static str> {
    let bytes = segment.as_bytes();
    if bytes.len() != 8
        || bytes[0] != b'L'
        || bytes[1] != b'['
        || bytes[3] != b','
        || bytes[5] != b','
        || bytes[7] != b']'
        || !(b'0'..=b'2').contains(&bytes[2])
        || !(b'0'..=b'2').contains(&bytes[4])
        || !(b'0'..=b'2').contains(&bytes[6])
    {
        return Err("invalid lattice address");
    }
    Ok((bytes[2] - b'0', bytes[4] - b'0', bytes[6] - b'0'))
}

fn parse_address(address: &str, max_depth: usize) -> Result<Vec<(u8, u8, u8)>, &'static str> {
    if !(1..=MAX_RECURSIVE_DEPTH).contains(&max_depth) {
        return Err("max_depth must be 1..8");
    }
    if address.is_empty() {
        return Err("address must be a non-empty string");
    }
    if address.len() > max_depth * 8 + (max_depth - 1) {
        return Err("address exceeds canonical length limit");
    }
    let parts: Vec<&str> = address.split('/').collect();
    if parts.len() > max_depth {
        return Err("address exceeds recursive depth limit");
    }
    parts.into_iter().map(parse_segment).collect()
}

fn json_string_array(values: &[String]) -> String {
    format!(
        "[{}]",
        values
            .iter()
            .map(|value| format!("\"{value}\""))
            .collect::<Vec<_>>()
            .join(",")
    )
}

fn conformance_payload_json() -> String {
    let lex = lexicographic_cells();
    let phi = phi_stride_cells();
    format!(
        concat!(
            "{{",
            "\"lexicographic_cells\":{},",
            "\"lexicographic_traversal_id\":\"{}\",",
            "\"max_address_length\":{},",
            "\"max_recursive_depth\":{},",
            "\"modulus\":{},",
            "\"phi_stride\":{},",
            "\"phi_stride_cells\":{},",
            "\"phi_traversal_id\":\"{}\",",
            "\"profile_id\":\"{}\",",
            "\"protocol\":\"{}\"",
            "}}"
        ),
        json_string_array(&lex),
        LEXICOGRAPHIC_TRAVERSAL,
        MAX_ADDRESS_LENGTH,
        MAX_RECURSIVE_DEPTH,
        TOP_LEVEL_CELL_COUNT,
        PHI_STRIDE,
        json_string_array(&phi),
        PHI_STRIDE_TRAVERSAL,
        PROFILE_ID,
        CONFORMANCE_PROTOCOL,
    )
}

const SHA256_INITIAL: [u32; 8] = [
    0x6a09e667,
    0xbb67ae85,
    0x3c6ef372,
    0xa54ff53a,
    0x510e527f,
    0x9b05688c,
    0x1f83d9ab,
    0x5be0cd19,
];

const SHA256_K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

fn sha256(input: &[u8]) -> [u8; 32] {
    let mut state = SHA256_INITIAL;
    let bit_len = (input.len() as u64) * 8;
    let mut data = input.to_vec();
    data.push(0x80);
    while data.len() % 64 != 56 {
        data.push(0);
    }
    data.extend_from_slice(&bit_len.to_be_bytes());

    for chunk in data.chunks_exact(64) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            let j = i * 4;
            w[i] = u32::from_be_bytes([chunk[j], chunk[j + 1], chunk[j + 2], chunk[j + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7)
                ^ w[i - 15].rotate_right(18)
                ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17)
                ^ w[i - 2].rotate_right(19)
                ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }

        let mut a = state[0];
        let mut b = state[1];
        let mut c = state[2];
        let mut d = state[3];
        let mut e = state[4];
        let mut f = state[5];
        let mut g = state[6];
        let mut h = state[7];

        for i in 0..64 {
            let big1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let choose = (e & f) ^ ((!e) & g);
            let temp1 = h
                .wrapping_add(big1)
                .wrapping_add(choose)
                .wrapping_add(SHA256_K[i])
                .wrapping_add(w[i]);
            let big0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let majority = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = big0.wrapping_add(majority);

            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        state[0] = state[0].wrapping_add(a);
        state[1] = state[1].wrapping_add(b);
        state[2] = state[2].wrapping_add(c);
        state[3] = state[3].wrapping_add(d);
        state[4] = state[4].wrapping_add(e);
        state[5] = state[5].wrapping_add(f);
        state[6] = state[6].wrapping_add(g);
        state[7] = state[7].wrapping_add(h);
    }

    let mut output = [0u8; 32];
    for (index, word) in state.iter().enumerate() {
        output[index * 4..index * 4 + 4].copy_from_slice(&word.to_be_bytes());
    }
    output
}

fn hex_lower(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{byte:02x}")).collect()
}

fn profile_fingerprint() -> String {
    format!("sha256:{}", hex_lower(&sha256(conformance_payload_json().as_bytes())))
}

fn conformance_record_json() -> String {
    let payload = conformance_payload_json();
    format!("{{\"fingerprint\":\"{}\",{}", profile_fingerprint(), &payload[1..])
}

fn self_check() {
    let lex = lexicographic_cells();
    let phi = phi_stride_cells();
    assert_eq!(lex.first().map(String::as_str), Some("L[0,0,0]"));
    assert_eq!(lex.last().map(String::as_str), Some("L[2,2,2]"));
    assert_eq!(phi[1], "L[1,2,2]");
    assert_eq!(parse_address("L[2,0,1]/L[1,1,0]", 8).unwrap().len(), 2);
    assert!(parse_address("L[3,0,0]", 8).is_err());
    assert!(parse_address("L[0,0,0]//L[1,1,1]", 8).is_err());
    assert!(parse_address("L[0,0,0]/L[1,1,1]", 1).is_err());
    assert_eq!(profile_fingerprint(), EXPECTED_FINGERPRINT);
}

fn main() {
    self_check();
    println!("{}", conformance_record_json());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn traversals_are_27_cell_bijections() {
        let lex = lexicographic_cells();
        let phi = phi_stride_cells();
        assert_eq!(lex.len(), 27);
        assert_eq!(phi.len(), 27);
        assert_eq!(lex.iter().collect::<HashSet<_>>().len(), 27);
        assert_eq!(phi.iter().collect::<HashSet<_>>().len(), 27);
        assert_eq!(lex.iter().collect::<HashSet<_>>(), phi.iter().collect::<HashSet<_>>());
    }

    #[test]
    fn recursive_address_parser_is_strict_and_bounded() {
        assert!(parse_address("L[0,0,0]", 8).is_ok());
        assert!(parse_address("L[0,0,0]/L[2,2,2]", 8).is_ok());
        assert!(parse_address("L[3,0,0]", 8).is_err());
        assert!(parse_address("../L[0,0,0]", 8).is_err());
        assert!(parse_address("L[0,0,0]//L[1,1,1]", 8).is_err());
    }

    #[test]
    fn canonical_fingerprint_matches_v1() {
        assert_eq!(profile_fingerprint(), EXPECTED_FINGERPRINT);
    }
}
