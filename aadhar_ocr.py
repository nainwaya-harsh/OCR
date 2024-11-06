import cv2
import pytesseract
import re

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    # Load the image
    img = cv2.imread(image_path)
    
    # Resize image for better OCR accuracy
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast by histogram equalization
    gray = cv2.equalizeHist(gray)
    
    # Apply GaussianBlur to reduce noise and improve OCR
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Sharpening the image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    sharp = cv2.filter2D(gray, -1, kernel)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return thresh

def extract_aadhar_details(image_path):
    # Preprocess the image
    processed_image = preprocess_image(image_path)
    
    # Perform OCR on the processed image
    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(processed_image, config=config)
    
    # Print the OCR output for debugging
    print("Full OCR Output:\n", text)

    # Initialize dictionary for Aadhaar details
    details = {
        "Aadhar Number": None,
        "Name": None,
        "DOB": None,
        "Gender": None,
        "Mobile Number": None,
    }

    # Clean the OCR output text
    cleaned_text = re.sub(r"[^A-Za-z0-9\s:/\n]", "", text)  # Remove special characters
    lines = cleaned_text.splitlines()

    # Extract Aadhaar number
    aadhar_number_match = re.search(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", cleaned_text)
    if aadhar_number_match:
        details["Aadhar Number"] = aadhar_number_match.group(0)

    # Extract Date of Birth (DOB)
    dob_match = re.search(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", cleaned_text)
    if dob_match:
        details["DOB"] = dob_match.group(0)

    # Extract gender
    if re.search(r"\bMALE\b", cleaned_text, re.IGNORECASE):
        details["Gender"] = "Male"
    elif re.search(r"\bFEMALE\b", cleaned_text, re.IGNORECASE):
        details["Gender"] = "Female"

    # Extract mobile number
    mobile_match = re.search(r"\b\d{10}\b", cleaned_text)
    if mobile_match:
        details["Mobile Number"] = mobile_match.group(0)

    # Extract name by finding the line after "Government of India"
    for i, line in enumerate(lines):
        if "Government of India" in line or "GOVERNMENT OF INDIA" in line:
            if i + 1 < len(lines):
                potential_name = lines[i + 1].strip()
                # Check if it's a likely name
                if re.match(r"^[A-Za-z\s]+$", potential_name):
                    details["Name"] = potential_name
            break

    return details

# Test the function
image_path = r"D:\kustodian\OCR\harsh_aadhar.jpg"  # Replace with the actual path
aadhar_details = extract_aadhar_details(image_path)

print("\nExtracted Aadhaar Details:")
for key, value in aadhar_details.items():
    print(f"{key}: {value}")
