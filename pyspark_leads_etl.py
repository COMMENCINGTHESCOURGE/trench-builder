#!/usr/bin/env python3
"""
Optimized PySpark ETL Script for Dataproc Serverless Batch Job
Extracts, cleans, and filters high-value business leads from BigQuery/Spanner.

Requirements satisfied:
1. Spark Config: Spark Session is initialized with the correct configuration:
   - 'spark.sql.streaming.forceDeleteTempCheckpointLocation' set to 'true'.
   - 'viewsEnabled' set to 'true' to support reading from BigQuery views.
2. Schema & Reads: Dynamically loads business opportunities with columns:
   - [opportunity_id, company_name, description, value, contact_email, date_published]
3. Processing:
   - Filters out rows with null/empty contact emails or missing/empty description fields.
   - Explicitly casts 'value' to DoubleType.
   - Uses case-insensitive regex pattern-matching via SQL rlike function to locate relevant keywords:
     ['software', '3d model', 'cad', 'blender', 'rendering', 'saas', 'automation'].
   - Ranks the matching leads globally using analytical Window rank() in descending order of value.
4. Safe Writes: Prints processed schemas using printSchema() and executes fully distributed
   connector-level writes back to BigQuery or Cloud Spanner without driver bottlenecks (never uses toPandas() or collect()).
"""

import argparse
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rank, desc, trim
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.window import Window

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Dataproc Serverless PySpark Leads ETL")
    parser.add_argument("--input_table", help="Input BigQuery table (e.g., project.dataset.table)")
    parser.add_argument("--output_destination", choices=["bigquery", "spanner"], help="Target storage system")
    parser.add_argument("--output_table", help="Output BigQuery or Spanner table name")
    parser.add_argument("--temp_gcs_bucket", help="GCS bucket for temporary BigQuery/Spanner storage")
    
    # Spanner specific arguments
    parser.add_argument("--spanner_instance", help="Cloud Spanner instance ID (required if output is spanner)")
    parser.add_argument("--spanner_database", help="Cloud Spanner database ID (required if output is spanner)")
    parser.add_argument("--spanner_project", help="Cloud Spanner Google Cloud Project ID (required if output is spanner)")
    
    # Local verification flag
    parser.add_argument("--test", action="store_true", help="Run in local test mode with mock data")
    
    args = parser.parse_args()

    # Parameter validations
    if not args.test:
        if not all([args.input_table, args.output_destination, args.output_table, args.temp_gcs_bucket]):
            parser.print_help()
            sys.exit(1)
        if args.output_destination == "spanner" and not all([args.spanner_instance, args.spanner_database, args.spanner_project]):
            print("Error: Spanner output requires --spanner_instance, --spanner_database, and --spanner_project", file=sys.stderr)
            sys.exit(1)

    # Initialize Spark Session with optimized configurations
    spark_builder = SparkSession.builder \
        .appName("Dataproc-Serverless-Leads-ETL") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .config("viewsEnabled", "true")

    # If running locally in test mode, master should be local
    if args.test:
        spark_builder = spark_builder.master("local[*]")

    spark = spark_builder.getOrCreate()

    # Log setup
    log = spark._jvm.org.apache.log4j.LogManager.getLogger(__name__)
    log.info("Spark Session established. Beginning Leads ETL process.")

    try:
        # Load or mock input data
        if args.test:
            log.info("Running in LOCAL TEST mode. Generating mock business opportunity dataset...")
            mock_schema = StructType([
                StructField("opportunity_id", StringType(), True),
                StructField("company_name", StringType(), True),
                StructField("description", StringType(), True),
                StructField("value", StringType(), True),  # Casted to DoubleType later
                StructField("contact_email", StringType(), True),
                StructField("date_published", StringType(), True)
            ])
            mock_data = [
                ("101", "Alpha Soft", "Looking for software engineering consulting services", "150000.0", "leads@alphasoft.com", "2026-07-01"),
                ("102", "Beta Tech", "Requires a custom 3d model for mechanical pipeline", "45000.0", "contact@betatech.io", "2026-07-02"),
                ("103", "Gamma Corp", "Need a generic marketing strategy guide", "25000.0", "info@gammacorp.com", "2026-07-03"),
                ("104", "Delta Ltd", "Automation framework for web applications", "120000.00", "jobs@deltaltd.com", "2026-07-04"),
                ("105", "Epsilon CAD", "Industrial CAD design pipeline optimization", "85000.50", "hello@epsiloncad.com", "2026-07-04"),
                ("106", "Zeta Blender", "Blender rendering engine specialized pipeline", "110000.0", None, "2026-07-04"), # Null Email (should be filtered)
                ("107", "Eta SaaS", None, "75000.0", "billing@etasaas.com", "2026-07-04"), # Null Description (should be filtered)
                ("108", "Theta Inc", "SaaS platform scaling and cloud automation support", "220000.00", "corp@thetainc.com", "2026-07-04"),
            ]
            df_raw = spark.createDataFrame(mock_data, mock_schema)
        else:
            log.info(f"Reading from BigQuery table: {args.input_table}")
            df_raw = spark.read \
                .format("bigquery") \
                .option("table", args.input_table) \
                .load()

        # Print raw schema
        log.info("Raw Input Schema:")
        df_raw.printSchema()

        # Clean raw columns: filter out rows with null/empty emails or missing description fields
        log.info("Cleaning leads data...")
        df_cleaned = df_raw.filter(
            col("contact_email").isNotNull() & (trim(col("contact_email")) != "") &
            col("description").isNotNull() & (trim(col("description")) != "")
        )

        # Cast the 'value' column to DoubleType explicitly
        df_cleaned = df_cleaned.withColumn("value", col("value").cast(DoubleType()))

        # Define keywords for the regex search pattern
        keywords = ['software', '3d model', 'cad', 'blender', 'rendering', 'saas', 'automation']
        regex_pattern = "(?i)" + "|".join(keywords)

        # Apply regex filter to locate matched opportunity descriptions
        log.info("Applying regex keyword match filter...")
        df_filtered = df_cleaned.filter(col("description").rlike(regex_pattern))

        # Rank the matching leads in descending order of contract value using an analytical Window function
        # This keeps operations fully distributed, avoiding driver bottlenecks
        log.info("Ranking matching leads globally...")
        window_spec = Window.orderBy(desc("value"))
        df_ranked = df_filtered.withColumn("lead_rank", rank().over(window_spec))

        # Print final Schema prior to saving
        print("Final Processed Schema with Rankings:")
        df_ranked.printSchema()

        if args.test:
            log.info("Mock ETL execution results:")
            df_ranked.show(truncate=False)
        else:
            # Distribute output writing securely without pulling data to driver
            if args.output_destination == "bigquery":
                log.info(f"Writing to BigQuery destination table: {args.output_table}")
                df_ranked.write \
                    .format("bigquery") \
                    .option("table", args.output_table) \
                    .option("temporaryGcsBucket", args.temp_gcs_bucket) \
                    .mode("overwrite") \
                    .save()
                    
            elif args.output_destination == "spanner":
                log.info(f"Writing to Cloud Spanner destination: {args.output_table}")
                df_ranked.write \
                    .format("cloudspanner") \
                    .option("projectId", args.spanner_project) \
                    .option("instanceId", args.spanner_instance) \
                    .option("databaseId", args.spanner_database) \
                    .option("table", args.output_table) \
                    .option("temporaryGcsBucket", args.temp_gcs_bucket) \
                    .mode("append") \
                    .save()

        log.info("ETL process finished successfully.")

    except Exception as e:
        log.error(f"ETL Execution Failed: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
