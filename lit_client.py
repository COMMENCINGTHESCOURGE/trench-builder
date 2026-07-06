import requests
import json
import base64
import numpy as np

API_URL = "http://127.0.0.1:8000/predict"

def test_terrain_api_streaming():
    payload = {
        "coords": [
            [10.5, 20.0, 30.0],
            [11.2, 21.5, 31.0],
            [12.0, 22.0, 32.0],
            [13.5, 23.0, 33.0]
        ]
    }

    print(f"Sending request to {API_URL} with payload: {payload}")

    try:
        response = requests.post(API_URL, json=payload, stream=True)
        response.raise_for_status()

        print("Received streamed response:")
        received_data = []
        for line in response.iter_lines():
            if line:
                try:
                    decoded_line = line.decode("utf-8")
                    chunk_data = json.loads(decoded_line)
                    
                    # Decode the base64 binary payload
                    b64_string = chunk_data.get('chunk_data', '')
                    raw_bytes = base64.b64decode(b64_string)
                    
                    # Reconstruct the tensor
                    shape = tuple(chunk_data.get('shape', []))
                    dtype = chunk_data.get('dtype', 'float32')
                    tensor = np.frombuffer(raw_bytes, dtype=dtype).reshape(shape)
                    
                    print(f"  Received valid tensor of shape: {tensor.shape}, Memory size: {tensor.nbytes / 1024:.2f} KB")
                    received_data.append(tensor)
                except json.JSONDecodeError:
                    print(f"  Error decoding JSON envelope: {line.decode('utf-8')}")
                except Exception as e:
                    print(f"  Error processing chunk: {e}")
        
        print(f"\nSuccessfully received and decoded {len(received_data)} binary chunks.")

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the LitServe API at {API_URL}.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_terrain_api_streaming()
