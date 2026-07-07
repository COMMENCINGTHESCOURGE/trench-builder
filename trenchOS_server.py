#!/usr/bin/env python3
import asyncio
import websockets
import json
import math
import time
from full_suit_mechanics import (
    MOBILITY_INTERFACE,
    WEAPONS_INTERFACE,
    POWER_INTERFACE,
    THERMAL_INTERFACE,
    SUIT_CONSTRAINTS_V3
)

# TrenchOS Game State
state = {
    "x": 0.0,
    "y": 10.0,
    "z": 0.0,
    "vx": 0.0,
    "vy": 0.0,
    "vz": 0.0,
    "pitch": 0.0, # Not strictly 2D but needed for the camera
    "yaw": 0.0,
    "activeWeapon": 1,
    "onGround": False,
    "speed": 0.0,
    
    # Subsystem constraints
    "heat_c": THERMAL_INTERFACE.state["current_temp_c"],
    "max_heat_c": THERMAL_INTERFACE.state["max_temp_c"],
    "power_j": POWER_INTERFACE.state["current_j"],
    "max_power_j": POWER_INTERFACE.state["capacity_j"],
    "mass_kg": 249.0
}

# Input state
inputs = {
    "forward": False,
    "backward": False,
    "left": False,
    "right": False,
    "jump": False
}

GRAVITY = -15.0
JUMP_VEL = 7.0
BASE_MOVE_SPEED = SUIT_CONSTRAINTS_V3["target_speed_ms"]
LAST_TICK = time.time()

async def handle_client(websocket, path=None):
    global inputs, state
    print("[TrenchOS] Client connected.")
    
    # Send initial state
    await websocket.send(json.dumps({"type": "init", "state": state}))
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data["type"] == "input":
                    inputs.update(data["keys"])
                elif data["type"] == "camera":
                    state["pitch"] = data.get("pitch", state["pitch"])
                    state["yaw"] = data.get("yaw", state["yaw"])
                elif data["type"] == "action":
                    if data["action"] == "switchWeapon":
                        state["activeWeapon"] = data["weapon"]
                        print(f"[TrenchOS] Switched to weapon {state['activeWeapon']}")
                    elif data["action"] == "fire":
                        # Weapon draws power and creates heat
                        power_draw = WEAPONS_INTERFACE.power_draw_w
                        if state["power_j"] >= power_draw:
                            state["power_j"] -= power_draw
                            state["heat_c"] += 2.0
                            print(f"[TrenchOS] Fired weapon. Heat: {state['heat_c']:.1f}C")
                        else:
                            print("[TrenchOS] Insufficient power to fire!")
            except Exception as e:
                print(f"[TrenchOS] Error parsing message: {e}")
    except websockets.exceptions.ConnectionClosed:
        print("[TrenchOS] Client disconnected.")

async def game_loop():
    global LAST_TICK, state, inputs
    
    while True:
        now = time.time()
        dt = now - LAST_TICK
        LAST_TICK = now
        
        # We need a small dt protection
        if dt > 0.1: dt = 0.1
        
        # --- PHYSICS & MOBILITY ---
        # 1. Player Intent -> Force
        dx = 0
        dz = 0
        if inputs.get("forward"): dz -= 1
        if inputs.get("backward"): dz += 1
        if inputs.get("left"): dx -= 1
        if inputs.get("right"): dx += 1
        
        # Normalize input vector
        mag = math.hypot(dx, dz)
        if mag > 0:
            dx /= mag
            dz /= mag
            
        # Transform by yaw (AURORA sends yaw)
        sinY = math.sin(state["yaw"])
        cosY = math.cos(state["yaw"])
        
        # Movement velocity target
        # Knee bottleneck: limits speed based on mass
        mass_penalty = max(1.0, state["mass_kg"] / 200.0)
        speed_target = BASE_MOVE_SPEED / mass_penalty
        
        tx = (cosY * dx + sinY * dz) * speed_target
        tz = (-sinY * dx + cosY * dz) * speed_target
        
        # Acceleration/Friction
        if state["onGround"]:
            state["vx"] = state["vx"] + (tx - state["vx"]) * 10.0 * dt
            state["vz"] = state["vz"] + (tz - state["vz"]) * 10.0 * dt
            if inputs.get("jump"):
                state["vy"] = JUMP_VEL
                state["onGround"] = False
                state["power_j"] -= MOBILITY_INTERFACE.power_draw_w * 2  # Jump costs power
        else:
            state["vx"] = state["vx"] + (tx - state["vx"]) * 2.0 * dt
            state["vz"] = state["vz"] + (tz - state["vz"]) * 2.0 * dt
            
        # Gravity
        state["vy"] += GRAVITY * dt
        
        # Position update
        state["x"] += state["vx"] * dt
        state["y"] += state["vy"] * dt
        state["z"] += state["vz"] * dt
        
        # Terrain collision (Mock for now, normally calls GhostCollider)
        # Assuming floor is at y=10
        if state["y"] < 10.0:
            state["y"] = 10.0
            state["vy"] = 0
            state["onGround"] = True
            
        state["speed"] = math.hypot(state["vx"], state["vz"])
        
        # --- VINCULUM SYSTEMS ---
        # Power & Thermal tick
        if state["speed"] > 0.1:
            state["power_j"] -= MOBILITY_INTERFACE.power_draw_w * dt
            state["heat_c"] += 0.5 * dt
            
        # Thermal dissipation
        cooling_rate = THERMAL_INTERFACE.state["radiator_efficiency"] * 5.0
        if state["heat_c"] > 35.0:
            state["heat_c"] -= cooling_rate * dt
        
        # Enforce bounds
        state["heat_c"] = min(max(state["heat_c"], 35.0), state["max_heat_c"])
        state["power_j"] = max(state["power_j"], 0.0)
        
        await asyncio.sleep(1/60) # 60 Hz tick

async def broadcast_state():
    """Broadcasts the game state to all connected clients."""
    while True:
        # We need the active connections from the server.
        # It's easier to iterate through the active websocket connections.
        if server and server.websockets:
            payload = json.dumps({"type": "state", "state": state})
            websockets.broadcast(server.websockets, payload)
        await asyncio.sleep(1/60)

async def main():
    global server
    print("[TrenchOS] Starting WebSocket Server on port 8765...")
    server = await websockets.serve(handle_client, "localhost", 8765)
    
    # Run the game loop and broadcast loop concurrently
    await asyncio.gather(
        game_loop(),
        broadcast_state(),
        server.wait_closed()
    )

if __name__ == "__main__":
    asyncio.run(main())
