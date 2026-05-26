import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder,StandardScaler
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class DataProcessing:
    def __init__(self,input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        self.features = None

        os.makedirs(self.output_path,exist_ok=True)
        logger.info("Data Processing initalized...")

    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_path)
            logger.info("Data loaded sucesfully...")
        except Exception as e:
            logger.error(f"Error while loading data {e}")
            raise CustomException("Failed to load data",e)
        
    def preprocess(self):
        try:
            if "Timestamp" in self.df.columns:
                self.df["Timestamp"] = pd.to_datetime(self.df["Timestamp"] , errors='coerce')
                self.df["Year"] = self.df["Timestamp"].dt.year
                self.df["Month"] = self.df["Timestamp"].dt.month
                self.df["Day"] = self.df["Timestamp"].dt.day
                self.df["Hour"] = self.df["Timestamp"].dt.hour
                self.df.drop(columns=["Timestamp"], inplace=True)
            elif "Installation_Year" in self.df.columns:
                self.df["Year"] = self.df["Installation_Year"]
                self.df["Month"] = 1
                self.df["Day"] = 1
                self.df["Hour"] = 0

            # Handle Categorical Columns defensively
            categorical_cols = ['Operation_Mode', 'Efficiency_Status', 'Machine_Type']
            found_categorical = [col for col in categorical_cols if col in self.df.columns]
            
            for col in found_categorical:
                self.df[col] = self.df[col].astype('category')
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col])

            if "Machine_ID" in self.df.columns:
                self.df.drop(columns=["Machine_ID"], inplace=True)

            logger.info(f"Preprocessing completed. Found columns: {list(self.df.columns)}")
        
        except Exception as e:
            logger.error(f"Error while preprocessing data {e}")
            raise CustomException("Failed to preprocess data",e)
        
    def split_and_scale_and_save(self):
        try:
            # Define available feature maps between schemas
            schema_map = {
                'Vibration_Hz': 'Vibration_mms',
                'Efficiency_Status': 'Failure_Within_7_Days'
            }

            self.features = [
                'Operation_Mode', 'Temperature_C', 'Vibration_Hz',
                'Power_Consumption_kW', 'Network_Latency_ms', 'Packet_Loss_%',
                'Quality_Control_Defect_Rate_%', 'Production_Speed_units_per_hr',
                'Predictive_Maintenance_Score', 'Error_Rate_%','Year', 'Month', 'Day', 'Hour'
            ]

            # Adjust features based on what's available in the current dataframe
            actual_features = []
            for f in self.features:
                if f in self.df.columns:
                    actual_features.append(f)
                elif f in schema_map and schema_map[f] in self.df.columns:
                    actual_features.append(schema_map[f])
            
            if not actual_features:
                # If no standard features found, try to use all numeric columns
                actual_features = self.df.select_dtypes(include=[np.number]).columns.tolist()
                if "Failure_Within_7_Days" in actual_features:
                    actual_features.remove("Failure_Within_7_Days")

            X = self.df[actual_features]
            
            # Identify target column
            target = "Efficiency_Status" if "Efficiency_Status" in self.df.columns else "Failure_Within_7_Days"
            if target not in self.df.columns:
                # Fallback to the last column if target not found
                target = self.df.columns[-1]
            
            y = self.df[target]

            logger.info(f"Using features: {actual_features}, Target: {target}")

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            X_train , X_test , y_train , y_test = train_test_split(X_scaled,y, test_size=0.2 , random_state=42)

            joblib.dump(X_train , os.path.join(self.output_path , "X_train.pkl"))
            joblib.dump(X_test , os.path.join(self.output_path , "X_test.pkl"))
            joblib.dump(y_train , os.path.join(self.output_path , "y_train.pkl"))
            joblib.dump(y_test , os.path.join(self.output_path , "y_test.pkl"))

            joblib.dump(scaler , os.path.join(self.output_path , "scaler.pkl"))
            logger.info("All things saved sucesfully for Data processing..")

        except Exception as e:
            logger.error(f"Error while split scale and save data {e}")
            raise CustomException("Failed to spli sacle and save data",e)
        
    def run(self):
        self.load_data()
        self.preprocess()
        self.split_and_scale_and_save()

if __name__=="__main__":
    processor = DataProcessing("artifacts/raw/data.csv" , "artifacts/processed")
    processor.run()