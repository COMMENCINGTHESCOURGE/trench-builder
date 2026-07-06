import litserve as ls
import torch
import numpy as np
import base64
import json
import sys

# Ensure TrenchOS is in path
sys.path.append(r'C:\Users\dasha\Projects\trenchos')
try:
    from trenchos_engine import TypingEngine
    GLOBAL_TYPING_ENGINE = TypingEngine(vocabulary={"density", "cohesion", "permeability", "water", "sediment", "oxidation"})
except ImportError:
    print("Warning: trenchos_engine not found. Autocomplete and payload validation disabled.")
    GLOBAL_TYPING_ENGINE = None

class TerrainGenerationAPI(ls.LitAPI):
    def setup(self, device):
        # Load your trained PyTorch model here.
        self.device = device
        self.typing_engine = GLOBAL_TYPING_ENGINE
        try:
            self.model = torch.load("terrain_generator.pt", map_location=device)
            self.model.eval()
            print(f"Model loaded successfully on {device}.")
        except FileNotFoundError:
            print("Warning: terrain_generator.pt not found. Using placeholder inference logic.")
            self.model = None

    def decode_request(self, request):
        coords = None
        valid_channels = []
        if isinstance(request, dict):
            coords = request.get("coords")
            channels = request.get("channels", [])
            
            # Validate and autocorrect channels using TrenchOS TypingEngine
            if self.typing_engine and channels:
                for ch in channels:
                    candidates = self.typing_engine.build_candidates(ch, threshold=2)
                    if candidates:
                        valid_channels.append(candidates[0]["word"])
                    else:
                        valid_channels.append(ch)
            else:
                valid_channels = channels

            if coords is not None:
                # Return tuple or dict. For batching, we return the coords, but attach channels for context if needed.
                return {"coords": coords, "channels": valid_channels}
            return request

        if isinstance(request, list):
            return {"coords": request, "channels": []}
            
        raise ValueError("Invalid request format. Expected 'coords' key or list.")

    def predict(self, batch_inputs):
        # batch_inputs will be a list of the returned values from decode_request
        # Assuming coords is what the model needs
        coords_list = [item["coords"] if isinstance(item, dict) else item for item in batch_inputs]
        coords = torch.tensor(coords_list, dtype=torch.float32, device=self.device)
        
        generated_data = []
        with torch.no_grad():
            if self.model is not None:
                outputs = self.model(coords)
                outputs = outputs.cpu().numpy()
                for i, tensor in enumerate(outputs):
                    # In a real scenario, you'd filter the output tensor by batch_inputs[i]["channels"]
                    generated_data.append(tensor)
            else:
                for _ in batch_inputs:
                    tensor = np.random.rand(6, 16, 16, 16).astype(np.float32)
                    generated_data.append(tensor)
        
        for tensor_data in generated_data:
            yield tensor_data

    def encode_response(self, output):
        tensor_bytes = output.tobytes()
        encoded_b64 = base64.b64encode(tensor_bytes).decode('utf-8')
        
        return json.dumps({
            "chunk_data": encoded_b64,
            "shape": list(output.shape),
            "dtype": "float32"
        })

if __name__ == "__main__":
    api = TerrainGenerationAPI(max_batch_size=8, batch_timeout=0.05, stream=True)
    server = ls.LitServer(
        api,
        devices="auto",
        workers_per_device=2
    )
    
    # Attach Autocomplete route for HVE
    @server.app.get("/autocomplete")
    def autocomplete(word: str = ""):
        if GLOBAL_TYPING_ENGINE is None:
            return {"candidates": []}
        return {"candidates": GLOBAL_TYPING_ENGINE.build_candidates(word, threshold=2)}

    # Add CORS Middleware for HVE Frontend
    from fastapi.middleware.cors import CORSMiddleware
    server.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    print("Starting MANIFOLD 6-Channel Tensor API (LitServe)...")
    server.run(port=8000)
