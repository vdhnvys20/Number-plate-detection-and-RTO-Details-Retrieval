from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
import cv2  # type: ignore
import imutils  # type: ignore
import numpy as np  # type: ignore
import pytesseract  # type: ignore
import requests  # type: ignore
import os
import json
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Path to Tesseract executable 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set up API credentials
api_key = "YOUR_API_KEY"  # Replaced with the API key
api_host = "rto-vehicle-information-verification-india.p.rapidapi.com"

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file:
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Detect the number plate and cropped image
        number_plate, cropped_image_path, number_plate_area = detect_number_plate(file_path)
        
        if number_plate:
            vehicle_details = get_vehicle_details(number_plate)
            return render_template('result.html', image_path=url_for('uploaded_file', filename=file.filename),
                                   cropped_image_path=url_for('uploaded_file', filename=os.path.basename(cropped_image_path)),
                                   number_plate=number_plate, vehicle_details=vehicle_details,
                                   number_plate_area=number_plate_area)
        else:
            return jsonify({"error": "Number plate not detected"})

def detect_number_plate(image_path):
    # Load the image
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    # Check if the image was successfully loaded
    if img is None:
        print(f"Error: Unable to open image file at {image_path}")
        return None, None, None
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply bilateral filter and adaptive thresholding
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    # Find contours
    contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    # Loop over contours to find a rectangle
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            break

    # Check if a contour was found
    if screenCnt is None:
        print("No contour detected")
        return None, None, None

    # Draw the contour on the image
    cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

    # Create a mask and draw the contour
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    new_image = cv2.bitwise_and(img, img, mask=mask)

    # Extract the region of interest
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

    # Apply additional preprocessing to the cropped image
    Cropped = cv2.GaussianBlur(Cropped, (3, 3), 0)
    _, Cropped = cv2.threshold(Cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR on the cropped image
    text = pytesseract.image_to_string(Cropped, config='--psm 11')
    number_plate = ''.join(e for e in text if e.isalnum())
    print("Detected license plate Number is:", number_plate)

    # Highlight number plate area on the original image
    img_with_rect = cv2.rectangle(img.copy(), (topy, topx), (bottomy, bottomx), (0, 255, 0), 2)

    # Save the modified image with highlighted number plate
    output_image_path = os.path.join(app.config['OUTPUT_FOLDER'], f"highlighted_{os.path.basename(image_path)}")
    cv2.imwrite(output_image_path, img_with_rect)

    return number_plate, output_image_path, (topx, topy, bottomx, bottomy)

def get_vehicle_details(reg_no):
    username = "YOUR_USERNAME"
    url = f"http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber={reg_no}&username={username}"
    url = url.replace(" ", "%20")
    
    response = requests.get(url)
    print(f"API Response: {response.text}")

    try:
        tree = ET.ElementTree(ET.fromstring(response.content))
        vehicle_json = tree.find('.//{http://regcheck.org.uk}vehicleJson').text
        vehicle_details = json.loads(vehicle_json)
        return vehicle_details
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return {"error": "Vehicle details not found"}

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
