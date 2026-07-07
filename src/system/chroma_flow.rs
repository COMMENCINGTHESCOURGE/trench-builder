//! trench-builder/src/system/chroma_flow.rs
//! GOVERNOR: consumed by pathfinder hopping via FFI, TS side via HyperpolyBridge.
#[derive(Debug, Clone, Copy)]
pub struct ChromaFlow {
    pub corridor: u8,
    pub color: [f32; 3],
    pub passes: u32,
}

impl ChromaFlow {
    pub const fn from_mod9(n: u8) -> Self {
        let (corridor, color) = match n % 9 {
            0 => (0u8, [1.0, 0.0, 0.0]),
            1 => (1u8, [0.0, 1.0, 0.0]),
            2 => (2u8, [1.0, 0.5, 0.0]),
            3 => (3u8, [1.0, 1.0, 0.0]),
            4 => (4u8, [0.0, 1.0, 0.2]),
            5 => (5u8, [0.0, 0.4, 1.0]),
            6 => (6u8, [0.3, 0.0, 1.0]),
            7 => (7u8, [0.6, 0.0, 0.8]),
            _ => (8u8, [0.4, 0.0, 1.0]),
        };
        Self { corridor, color, passes: 1 }
    }

    #[inline]
    pub fn step(&mut self) -> u8 {
        self.corridor = ((self.corridor as u16 * 3) % 9) as u8;
        self.passes += 1;
        self.corridor
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn x3_breach_from_corridor_one() {
        let mut f = ChromaFlow::from_mod9(1);
        assert_eq!(f.step(), 3); // -> BREACH in {0,3,6}
    }
    #[test]
    fn reel_invariant_preserves_passes() {
        let mut f = ChromaFlow::from_mod9(4);
        for _ in 0..7 { f.step(); }
        assert_eq!(f.passes, 8);
    }
}
