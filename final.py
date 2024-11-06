import cv2
import pytesseract
import re

# Link pytesseract to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if path is different

def clean_text(text):
    # Remove extra symbols and unnecessary characters, but keep colons, slashes, and letters for easier processing
    return re.sub(r"[^a-zA-Z0-9\s:/]", "", text)

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

def aadharPanOCR(image_path, cardType):
    if cardType == 'AADHAR':
        processed_image = preprocess_image(image_path)
        
        # Perform OCR on the processed image
        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(processed_image, config=config)
        
        # Print the OCR output for debugging
        # print("Full OCR Output (Aadhaar):\n", text)

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

    elif cardType == 'PAN':
        img = cv2.imread(image_path)
        
        # Step 2: Preprocess the image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)  # Apply Gaussian Blur to reduce noise
        _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Apply thresholding

        # Step 3: Perform OCR on the preprocessed image
        text = pytesseract.image_to_string(thresholded, config='--psm 6')  # Page segmentation mode 6

        # Clean up the OCR output to remove special characters and symbols
        text = clean_text(text)
        
        # Debug: Print the cleaned OCR text
        # print("Cleaned OCR Output (PAN):\n", text)

        # Step 4: Extract PAN details using regular expressions
        details = {
            "PAN Number": None,
            "Name": None,
            "Father's Name": None,
            "DOB": None
        }

        # PAN Number (Format: 5 letters, 4 digits, 1 letter, e.g., ABCDE1234F)
        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
        if pan_match:
            details["PAN Number"] = pan_match.group(0)

        # Date of Birth (DOB), format DD/MM/YYYY or DD-MM-YYYY
        dob_match = re.search(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", text)
        if dob_match:
            details["DOB"] = dob_match.group(0)

        # Extract Name and Father's Name based on keywords
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "Name" in line and "Father" not in line:
                # Name should be on the next line
                if i + 1 < len(lines):
                    name_line = lines[i + 1].strip()
                    # Clean up the extracted name to remove unwanted words
                    name_line = re.sub(r"[^A-Z\s]", "", name_line)  # Keep only uppercase letters and spaces
                    details["Name"] = name_line.strip()
            
            elif "Father" in line:
                # Father's name should be on the next line
                if i + 1 < len(lines):
                    father_name_line = lines[i + 1].strip()
                    # Clean up the extracted father's name
                    father_name_line = re.sub(r"[^A-Z\s]", "", father_name_line)  # Keep only uppercase letters and spaces
                    details["Father's Name"] = father_name_line.strip()

        return details


# Test the function with a PAN card
pan_details = aadharPanOCR("D:/kustodian/OCR/pan_card.jpeg", "PAN")
print("\nExtracted PAN Card Details:")
for key, value in pan_details.items():
    print(f"{key}: {value}")
aadhar_details=aadharPanOCR("D:\kustodian\OCR\harsh_aadhar.jpg","AADHAR")
print("\nExtracted Aadhar Card Details:")
for key, value in aadhar_details.items():
    print(f"{key}: {value}")
# Print the extracted PAN details

