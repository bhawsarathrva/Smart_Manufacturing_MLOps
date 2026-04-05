import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

mlflow.start_run()

n_estimators = 100
mlflow.log_param("n_estimators", n_estimators)

model = RandomForestClassifier(n_estimators=n_estimators)
model.fit(X_train, y_train)

pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

mlflow.log_metric("accuracy", accuracy)

mlflow.sklearn.log_model(model, "model")

mlflow.end_run()