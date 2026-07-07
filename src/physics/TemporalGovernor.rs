//! TemporalGovernor.rs
//! GOVERNOR: enforces scheduler ordering + step cap per world tick.
//! consumed by TemporalScheduler.ts via FFI + HyperpolyBridge.
pub struct TemporalGovernor {
    pub min_dt_s: f32,
    pub max_dt_s: f32,
    pub steps_remaining: u64,
    pub watchdog: u64,
}

impl TemporalGovernor {
    pub fn clamp(&mut self, requested: f32) -> f32 {
        let clamped = requested.clamp(self.min_dt_s, self.max_dt_s);
        if self.steps_remaining == 0 { return 0.0; }
        self.steps_remaining -= 1;
        self.watchdog = self.watchdog.saturating_add(1);
        clamped
    }

    pub fn watchdog_exceeded(&self, limit: u64) -> bool { self.watchdog > limit }
}
