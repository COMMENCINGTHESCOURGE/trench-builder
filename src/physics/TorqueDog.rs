//! TorqueDog.rs
//! GOVERNOR: physics moment application for mecha/chassis limbs.
//! consumed by StigmergicEmitter.ts via FFI boundary.
pub struct TorqueDog {
    pub max_torque: f32,
    pub damping: f32,
}

impl TorqueDog {
    pub fn apply(&self, angle: f32, velocity: f32) -> f32 {{
        let desired = -angle * 4.0;
        let mut torque = (desired - velocity).clamp(-self.max_torque, self.max_torque);
        torque -= velocity * self.damping;
        torque
    }}
}
