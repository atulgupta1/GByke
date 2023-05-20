from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'new_schema'
}

# API endpoint for processing the entered values
@app.route('/process', methods=['POST'])
def process_values():
    data = request.get_json()

    in_VIN = data.get('imei')
    in_model = data.get('model')
    in_dealer = data.get('retailer')
    
    print("in_VIN: ", in_VIN)
    print("in_model: ", in_model)
    print("in_dealer: ", in_dealer)
    
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Perform the necessary database queries based on the entered values
        # Prepare the SQL query
        query = "SELECT * FROM OEM_Database WHERE Dealer_Code = %s AND VIN = %s AND Model_Code = %s"

        # Execute the query with the provided parameters
        cursor.execute(query, (in_dealer, in_VIN, in_model))
        row = cursor.fetchone()

        print("row: ", row)
        
        if row is None:
            response_code = 2
            # Prepare the response
            response = {
                'response_code': response_code,
                'response_text': get_response_text(response_code)
            }
            return jsonify(response)
            
        pdi_no, model_code, vin, consignee_location, dealer_code, sold_value, verified_value = row

        # Print the values
        print("PDI Number: ", pdi_no)
        print("Model Code: ", model_code)
        print("VIN: ", vin)
        print("Consignee Location: ", consignee_location)
        print("Dealer Code: ", dealer_code)
        print("Sold Value: ", sold_value)
        print("Verified Value: ", verified_value)
        print(type(sold_value))
        print(type(verified_value))

        # Determine the response code based on the query results
        if sold_value == 1 or verified_value == 1:
            response_code = 3
        elif sold_value == 0 and verified_value == 0:
            print("sold_value = 0 and verified_value =0")
            response_code = 0
            # Prepare the SQL query for update
            query = "UPDATE OEM_Database SET Verified = %s, Sold = %s WHERE Dealer_Code = %s AND VIN = %s AND Model_Code = %s"
            new_verified_status = 1
            new_sold_status = 1
            # Execute the query with the provided values
            cursor.execute(query, (new_verified_status, new_sold_status, dealer_code, vin, model_code))

            # Commit the changes to the database
            conn.commit()

        else:
            response_code = 4

        # Prepare the response
        response = {
            'response_code': response_code,
            'response_text': get_response_text(response_code)
        }

        # Close the database connection
        cursor.close()
        conn.close()

        return jsonify(response)

    except mysql.connector.Error as error:
        return jsonify({'error': str(error)})

# Helper function to map response codes to response text
def get_response_text(response_code):
    response_text = {
        1: 'Device blocked for EMI Sourcing as this is not a Valid OEM Serial/IMEI Number',
        2: 'Device blocked for EMI Sourcing due to Model and Serial/IMEI Number Mismatch',
        3: 'Device blocked for EMI Sourcing as the device is already sold and activated',
        4: 'Device blocked for EMI Sourcing due to Invalid Channel',
        0: 'Device Validated Successfully - Serial/IMEI Number and Model Match'
    }
    return response_text.get(response_code, 'Unknown response code')

if __name__ == '__main__':
    app.run()
