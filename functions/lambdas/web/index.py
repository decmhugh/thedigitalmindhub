import os

def lambda_handler(event, context):
    try:
        # Define the path to the HTML file
        #os.path.join(os.path.dirname(__file__), )
        html_file_path = "websocket.html"
        
        # Read the HTML file
        with open(html_file_path, "r") as file:
            html_content = file.read()
        
        # Return the HTML content as the HTTP response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": html_content
        }
    except Exception as e:
        # Handle errors and return a 500 response
        print(str(e))
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": f"Error reading HTML file: {str(e)}"
        }
