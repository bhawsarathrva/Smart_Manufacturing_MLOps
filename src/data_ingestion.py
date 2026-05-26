import sys
import os
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, raw_data_path: str, output_path: str):
        self.raw_data_path = raw_data_path
        self.output_path = output_path
        logger.info(f"Data Ingestion initialized with raw source: {self.raw_data_path}")

    def ingest_data(self):
        try:
            logger.info(f"Loading raw data from {self.raw_data_path}...")
            if not os.path.exists(self.raw_data_path):
                raise FileNotFoundError(f"Raw data file not found at {self.raw_data_path}")
            
            # Load the data defensively
            df = pd.read_csv(self.raw_data_path)
            logger.info(f"Raw data successfully loaded. Shape: {df.shape}")

            # Ensure output directory exists
            output_dir = os.path.dirname(self.output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            logger.info(f"Saving ingested data to {self.output_path}...")
            df.to_csv(self.output_path, index=False)
            logger.info("Data ingestion completed successfully.")
            return self.output_path

        except Exception as e:
            logger.error(f"Error during data ingestion: {e}")
            raise CustomException("Failed in data ingestion stage", e)

if __name__ == "__main__":
    # Default ingestion targets
    ingestion = DataIngestion(
        raw_data_path="DATA/factory_sensor_simulator_2040.csv",
        output_path="artifacts/raw/data.csv"
    )
    ingestion.ingest_data()
