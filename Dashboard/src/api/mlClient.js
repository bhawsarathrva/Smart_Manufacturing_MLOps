export const predictMaintenance = async (data) => {
  const response = await fetch('/api/ml/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Prediction failed');
  }

  return response.json();
};