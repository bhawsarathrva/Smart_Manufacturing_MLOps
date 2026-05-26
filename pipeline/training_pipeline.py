from src.data_ingestion import DataIngestion
from src.data_processing import DataProcessing
from src.model_training import ModelTraining

if __name__=="__main__":
    ingestion = DataIngestion("DATA/factory_sensor_simulator_2040.csv", "artifacts/raw/data.csv")
    ingestion.ingest_data()

    processor = DataProcessing("artifacts/raw/data.csv" , "artifacts/processed")
    processor.run()

    trainer = ModelTraining("artifacts/processed/" , "artifacts/models/")
    trainer.run()