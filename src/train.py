import mlflow
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from logger import get_logger
from custom_exception import CustomException

logger = get_logger(__name__)

def train():
    try:
        processed_path = "artifacts/processed"
        logger.info("Loading processed data for training...")
        
        X_train = joblib.load(os.path.join(processed_path, "X_train.pkl"))
        X_test = joblib.load(os.path.join(processed_path, "X_test.pkl"))
        y_train = joblib.load(os.path.join(processed_path, "y_train.pkl"))
        y_test = joblib.load(os.path.join(processed_path, "y_test.pkl"))

        mlflow.start_run()

        n_estimators = 100
        mlflow.log_param("n_estimators", n_estimators)

        # Train model
        logger.info(f"Training RandomForest model with n_estimators: {n_estimators}")
        model = RandomForestClassifier(n_estimators=n_estimators)
        model.fit(X_train, y_train)

        # Evaluate
        pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, pred)
        logger.info(f"Model Training Complete. Accuracy: {accuracy}")

        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "model")

        mlflow.end_run()

    except Exception as e:
        logger.error(f"Error occurred in train.py: {e}")
        raise CustomException("Training failed in train.py", e)

if __name__ == "__main__":
    train()