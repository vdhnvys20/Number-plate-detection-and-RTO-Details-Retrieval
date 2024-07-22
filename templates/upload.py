    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RTO Vehicle Details and Retrieval System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                padding: 20px;
                margin: 0;
            }
            .header {
                background-size: contain;
                background-repeat: no-repeat;
                height: 200px; /* Adjust height as needed */
                text-align: center;
                padding-top: 20px;
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
            }
            form {
                max-width: 600px;
                margin: 0 auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            input[type=file] {
                margin-bottom: 10px;
            }
            input[type=submit] {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            input[type=submit]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="header">
                    <h1>RTO Vehicle Details and Retrieval</h1>
                   
        </div>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br>
            <input type="submit" value="Upload">
        </form>
        <hr style="position:relative; top: 250px;border-top: 2px solid black;">
        <h4 style="position:absolute; bottom:0; left:50%; ">&copy 2024</h4>
    </body>
    </html>
        
