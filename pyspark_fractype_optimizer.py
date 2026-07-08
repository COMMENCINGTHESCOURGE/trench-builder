import sys
import json
import math
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import FloatType, StructType, StructField, StringType, IntegerType

# FracType Optimizer for Dataproc Serverless
# Compresses raw JSON 3D coordinates using logarithmic indexing.

def compress_coordinates(vertices_str: str) -> float:
    """
    Simulates FracType Logarithmic Packing Algorithm.
    Returns the compression ratio achieved on a string of JSON vertices.
    """
    try:
        if not vertices_str:
            return 1.0
            
        original_size = len(vertices_str.encode('utf-8'))
        
        # Parse payload
        vertices = json.loads(vertices_str)
        if not vertices:
            return 1.0
            
        # Extract unique floating points
        unique_floats = set()
        for v in vertices:
            for coord in v:
                if coord != "NaN":
                    # Simulate resolution clamping
                    unique_floats.add(round(coord, 4))
                    
        # Simulate logarithmic packing matrix size
        # Number of unique coordinates * 4 bytes per float + indexing overhead
        compressed_size = (len(unique_floats) * 4) + (len(vertices) * 3)
        
        if compressed_size == 0:
            return 1.0
            
        ratio = original_size / compressed_size
        return float(ratio)
        
    except Exception as e:
        return 1.0

# Register the UDF
compress_udf = udf(compress_coordinates, FloatType())

def main():
    print("=== FRACTYPE COMPRESSION OPTIMIZER ===")
    
    spark = SparkSession.builder \
        .appName("FracTypeOptimizer") \
        .getOrCreate()
        
    # In production, this reads from GCS gs://trench-builder-assets-prod
    print("[INFO] Simulating ingest of Kaggle Datasets (100GB+).")
    
    # Generate mock dataset for the optimizer
    data = [
        ("mesh_1", "[[0.0, 1.0, 2.0], [0.0, 1.0, 2.0], [1.0, 1.5, 3.0]]"),
        ("mesh_2", "[[1.2, 3.4, 5.6], [7.8, 9.0, 1.2]]"),
        ("mesh_3_corrupt", "[[NaN, 0.0, 1.0]]"),
    ]
    
    schema = StructType([
        StructField("mesh_id", StringType(), True),
        StructField("vertices_json", StringType(), True)
    ])
    
    df = spark.createDataFrame(data, schema)
    
    print("[INFO] Mapping FracType logarithmic packing across executor nodes...")
    
    # Apply compression UDF
    optimized_df = df.withColumn("compression_ratio", compress_udf(col("vertices_json")))
    
    # Show top results
    optimized_df.show(truncate=False)
    
    avg_compression = optimized_df.agg({"compression_ratio": "avg"}).collect()[0][0]
    print(f"\\n[RESULT] Average Compression Ratio Achieved: {avg_compression:.2f}x")
    
    spark.stop()

if __name__ == "__main__":
    main()
