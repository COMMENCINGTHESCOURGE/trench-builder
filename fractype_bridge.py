import socket
import asyncio
import sys
import time
import json
from fractype_renderer_v2 import AutoCloseFraction, FracNode, MicroFrac

# Configuration
ASUS_UDP_IP = "0.0.0.0"
ASUS_UDP_PORT = 8001
MOTO_G_HOST = "127.0.0.1" # Using ADB forward
MOTO_G_PORT = 5555

class VinculumBridge:
    def __init__(self):
        self.asus_intent = "AWAITING_TORSION"
        self.moto_g_resistance = "AWAITING_COMPUTE"
        
        # Setup UDP socket for Asus
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((ASUS_UDP_IP, ASUS_UDP_PORT))
        self.udp_sock.setblocking(False)

        # We will connect to Moto G inside the async loop
        self.moto_reader = None
        self.moto_writer = None

    async def connect_to_moto_g(self):
        print(f"Connecting to Sovereign Compute Node at {MOTO_G_HOST}:{MOTO_G_PORT}...")
        while True:
            try:
                self.moto_reader, self.moto_writer = await asyncio.open_connection(MOTO_G_HOST, MOTO_G_PORT)
                print("CONNECTED TO SOVEREIGN COMPUTE (MOTO G)")
                break
            except Exception as e:
                print(f"Waiting for Moto G... {e}")
                await asyncio.sleep(1)

    async def listen_to_asus(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                data, addr = await loop.sock_recvfrom(self.udp_sock, 1024)
                payload = data.decode('utf-8').strip()
                if payload:
                    self.asus_intent = payload
                    # Forward intent to Moto G for computation
                    if self.moto_writer:
                        self.moto_writer.write((payload + "\\n").encode())
                        await self.moto_writer.drain()
            except BlockingIOError:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(0.01)

    async def listen_to_moto_g(self):
        while True:
            if self.moto_reader:
                try:
                    data = await self.moto_reader.readline()
                    if data:
                        self.moto_resistance = data.decode('utf-8').strip()
                    else:
                        # Connection closed
                        print("Lost connection to Moto G.")
                        self.moto_reader = None
                        self.moto_writer = None
                        await self.connect_to_moto_g()
                except Exception as e:
                    await asyncio.sleep(1)
            else:
                await asyncio.sleep(1)

    async def render_loop(self):
        # 60Hz rendering loop
        frame = 0
        while True:
            sys.stdout.write("\033[H\033[J") # Clear screen
            print("════════════════════════════════════════════════════════════")
            print(" VINCULUM BRIDGE — 2.5D GODOT ARCHITECTURE PIPELINE")
            print(" LAYER 1 (ASUS)   -> LAYER 0 (MOTO G) -> LAYER 2 (HP VICTUS)")
            print("════════════════════════════════════════════════════════════\\n")
            
            # Using FracType AutoClose injection (Role 1: Division/AutoClose)
            fraction_block = AutoCloseFraction.inject(self.asus_intent, getattr(self, 'moto_resistance', self.moto_g_resistance), "{")
            
            # Use FracNode for dynamic rendering (Role 2: Grouping)
            node = FracNode(self.asus_intent, getattr(self, 'moto_resistance', self.moto_g_resistance), depth=1)
            
            print("--- KINETIC VINCULUM STATE ---")
            print(f"RAW COMPOSITE: {fraction_block}")
            print("\\n--- FRACTYPE RENDER ---")
            print(node.render(focus=True))
            
            print(f"\\n[FRAME {frame}] Listening on UDP {ASUS_UDP_PORT} | TCP {MOTO_G_PORT}")
            frame += 1
            await asyncio.sleep(1/60.0)

    async def run(self):
        await self.connect_to_moto_g()
        await asyncio.gather(
            self.listen_to_asus(),
            self.listen_to_moto_g(),
            self.render_loop()
        )

if __name__ == "__main__":
    bridge = VinculumBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print("\\nBridge terminated.")
