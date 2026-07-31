import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

# Set the title of the Streamlit app
st.title("SuperKart Revenue Prediction")

# Section for online prediction
st.subheader("Online Prediction")

# Collect user input for property features
st.header("Product Details")

Product_Weight = st.number_input(
    "Product Weight (kg)", min_value=0.0, max_value=50.0, value=12.0, step=0.1
)

Product_Sugar_Content = st.selectbox(
    "Product Sugar Content",
    options=["Low Sugar", "Regular", "No Sugar"]
)

Product_Allocated_Area = st.number_input(
    "Product Allocated Area (proportion of store area)",
    min_value=0.0, max_value=1.0, value=0.07, step=0.001, format="%.3f"
)

Product_MRP = st.number_input(
    "Product MRP", min_value=0.0, max_value=500.0, value=150.0, step=1.0
)

Product_Id_char = st.selectbox(
    "Product Category (from Product ID prefix)",
    options=["FD", "NC", "DR"]   # Food, Non-Consumable, Drinks
)

Product_Type_Category = st.selectbox(
    "Product Type",
    options=[
        "Frozen Foods", "Dairy", "Canned", "Baking Goods", "Health and Hygiene",
        "Snack Foods", "Meat", "Household", "Hard Drinks", "Fruits and Vegetables",
        "Breads", "Soft Drinks", "Breakfast", "Others", "Starchy Foods", "Seafood"
    ]
)

st.header("Store Details")

Store_Size = st.selectbox(
    "Store Size",
    options=["Small", "Medium", "High"]
)

Store_Location_City_Type = st.selectbox(
    "Store Location City Type",
    options=["Tier 1", "Tier 2", "Tier 3"]
)

Store_Type = st.selectbox(
    "Store Type",
    options=["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]
)

Store_Age_Years = st.number_input(
    "Store Age (Years)", min_value=0, max_value=50, value=15, step=1
)

# Convert user input into a DataFrame
input_data = pd.DataFrame([{
    'Product_Weight': Product_Weight,
    'Product_Sugar_Content': Product_Sugar_Content,
    'Product_Allocated_Area': Product_Allocated_Area,
    'Product_MRP': Product_MRP,
    'Store_Size': Store_Size,
    'Store_Location_City_Type': Store_Location_City_Type,
    'Store_Type': Store_Type,
    'Product_Id_char': Product_Id_char,
    'Store_Age_Years': Store_Age_Years,
    'Product_Type_Category': Product_Type_Category

}])

# Make prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/revenue", json=input_data.to_dict(orient='records')[0])  # Send data to Flask API
    if response.status_code == 200:
        prediction = response.json()['Predicted Revenue (in dollars)']
        st.success(f"Predicted Revenue (in dollars): {prediction}")
    else:
        st.error("Unable to connect to the prediction API.")

# Section for batch prediction
st.subheader("Batch Prediction")

# Allow users to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Make batch prediction when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        response = requests.post(f"{BACKEND_URL}/v1/revenuebatch", files={"file": uploaded_file})  # Send file to Flask API
        if response.status_code == 200:
            predictions = response.json()
            st.success("Batch predictions completed!")
            st.write(predictions)  # Display the predictions
        else:
            st.error("Unable to connect to the prediction API.")
