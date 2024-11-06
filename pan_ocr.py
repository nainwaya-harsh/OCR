import pytesseract
import re
import cv2

# Link pytesseract to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if path is different

def clean_text(text):
    # Remove extra symbols and unnecessary characters, but keep colons, slashes, and letters for easier processing
    return re.sub(r"[^a-zA-Z0-9\s:/]", "", text)

def extract_pan_details(image_path):
    # Step 1: Load the image
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
    print("Cleaned OCR Output:\n", text)

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

# Test the function with the provided PAN card image path
image_path = "D:/kustodian/OCR/pan_card.jpeg"  # Replace with the actual path to your PAN card image
pan_details = extract_pan_details(image_path)

# Print the extracted PAN details
print("\nExtracted PAN Card Details:")
for key, value in pan_details.items():
    print(f"{key}: {value}")
