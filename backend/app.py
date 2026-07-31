# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
revenue_predictor_api = Flask("SuperKart Future Revenue Predictor")

# Load the trained machine learning model
model = joblib.load("SuperKart_IM_model_v1_0.joblib")

# Define a route for the home page (GET request)
@revenue_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Revenue Prediction API!"

# Define an endpoint for single store revenue prediction (POST request)
@revenue_predictor_api.post('/v1/revenue')
def predict_revenue():
    """
    This function handles POST requests to the '/v1/revenue' endpoint.
    It expects a JSON payload containing each store details and returns
    the predicted Revenue as a JSON response.
    """
    # Get the JSON data from the request body
    stores_data = request.get_json()

    # Extract relevant features from the JSON data
    # Ensure column names match the features used for training X
    sample = {
        'Product_Weight': stores_data['Product_Weight'],
        'Product_Sugar_Content': stores_data['Product_Sugar_Content'],
        'Product_Allocated_Area': stores_data['Product_Allocated_Area'],
        'Product_MRP': stores_data['Product_MRP'],
        'Store_Size': stores_data['Store_Size'],
        'Store_Location_City_Type': stores_data['Store_Location_City_Type'],
        'Store_Type': stores_data['Store_Type'],
        'Product_Id_char': stores_data['Product_Id_char'],
        'Store_Age_Years': stores_data['Store_Age_Years'],
        'Product_Type_Category': stores_data['Product_Type_Category']
    }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make Predictions for one store
    predicted_revenue = model.predict(input_data)[0]

    # Convert predicted_price to Python float
    predicted_revenue = round(float(predicted_revenue), 2)
    # The conversion above is needed as we convert the model prediction (log price) to actual price using np.exp, which returns predictions as NumPy float32 values.
    # When we send this value directly within a JSON response, Flask's jsonify function encounters a datatype error

    # Return the actual price
    return jsonify({'Predicted Revenue (in dollars)': predicted_revenue})


# Define an endpoint for batch prediction (POST request)
@revenue_predictor_api.post('/v1/revenuebatch')
def predict_revenue_batch():
    """
    This function handles POST requests to the '/v1/revenuebatch' endpoint.
    It expects a CSV file containing property details for multiple properties
    and returns the predicted rental prices as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data_df = pd.read_csv(file)

    # Store_Id is needed for output but not for prediction, so store it if present
    store_ids = None
    if 'Store_Id' in input_data_df.columns:
        store_ids = input_data_df['Store_Id'].tolist()

    # Drop 'Product_Id', 'Product_Type', 'Store_Id' as these were dropped during training
    cols_to_drop = [col for col in ['Product_Id', 'Product_Type', 'Store_Id'] if col in input_data_df.columns]
    input_data_for_prediction = input_data_df.drop(columns=cols_to_drop, errors='ignore')

    # Make predictions for all stores in the DataFrame
    predicted_revenue_raw = model.predict(input_data_for_prediction) # Predict using data without dropped columns

    # Convert predicted_revenue to Python list of floats and round
    predicted_revenue_list = [round(float(rev), 2) for rev in predicted_revenue_raw]

    # Create a dictionary of predictions with store IDs as keys, or use indices if no Store_Id was provided
    if store_ids is None:
        store_ids = list(range(len(input_data_df)))
    output_dict = dict(zip(store_ids, predicted_revenue_list))

    # Return the predictions dictionary as a JSON response
    return jsonify(output_dict)

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    rental_price_predictor_api.run(debug=True)
