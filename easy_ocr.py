import pytesseract
import re
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def extract_card_details(image_path, card_type="aadhar"):
    # Initialize EasyOCR reader with English language
    reader = easyocr.Reader(['en'])
    
    # Read the image
    img = cv2.imread(image_path)
    
    # Perform OCR on the image
    result = reader.readtext(img, detail=0)  # Get text without bounding box details
    
    # Join all detected text into a single string
    text = "\n".join(result)

    # Dictionary to store extracted details
    details = {}

    # Define patterns and extraction logic based on card type
    if card_type.lower() == "aadhar":
        # Extract details specific to Aadhar card
        details = {
            "Aadhar Number": None,
            "Name": None,
            "DOB": None,
            "Gender": None,
            "Mobile Number": None
        }

        # Find Aadhar number (pattern like XXXX XXXX XXXX)
        aadhar_number_match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
        if aadhar_number_match:
            details["Aadhar Number"] = aadhar_number_match.group(0)

        # Find Date of Birth (DOB), format DD/MM/YYYY or DD-MM-YYYY
        dob_match = re.search(r"\bDOB[:\s]*\d{2}[-/]\d{2}[-/]\d{4}\b", text)
        if dob_match:
            details["DOB"] = dob_match.group(0).replace("DOB:", "").strip()

        # Identify gender (Male/Female) in text
        if "MALE" in text.upper():
            details["Gender"] = "Male"
        elif "FEMALE" in text.upper():
            details["Gender"] = "Female"

        # Extract mobile number (10-digit number pattern)
        mobile_match = re.search(r"\b\d{10}\b", text)
        if mobile_match:
            details["Mobile Number"] = mobile_match.group(0)

        # Extract name based on location of keywords
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "DOB" in line or "Gender" in line:
                # The name is often right above DOB or Gender
                if i - 1 >= 0:
                    name_line = lines[i - 1].strip()
                    if name_line and len(name_line.split()) >= 2:  # Check if it's likely a name
                        details["Name"] = name_line
                break

    elif card_type.lower() == "pan":
        # Extract details specific to PAN card
        details = {
            "PAN Number": None,
            "Name": None,
            "Father's Name": None,
            "DOB": None
        }

        # PAN number format: 5 uppercase letters followed by 4 digits and 1 uppercase letter (e.g., ABCDE1234F)
        pan_number_match = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
        if pan_number_match:
            details["PAN Number"] = pan_number_match.group(0)

        # Find Date of Birth (DOB), format DD/MM/YYYY or DD-MM-YYYY
        dob_match = re.search(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", text)
        if dob_match:
            details["DOB"] = dob_match.group(0).strip()

        # Extract name based on the assumption of PAN card layout
        # Usually, the name is the first prominent text followed by father's name and DOB
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "INCOME TAX DEPARTMENT" in line or "PERMANENT ACCOUNT NUMBER" in line:
                # The name is typically on the line below the keyword
                if i + 1 < len(lines):
                    name_line = lines[i + 1].strip()
                    # Clean up extracted name to remove extra noise
                    name_line = re.sub(r"[^A-Z\s]", "", name_line)
                    details["Name"] = name_line.strip()
                
                # Father's name typically follows the name
                if i + 2 < len(lines):
                    father_name_line = lines[i + 2].strip()
                    father_name_line = re.sub(r"[^A-Z\s]", "", father_name_line)
                    details["Father's Name"] = father_name_line.strip()
                
                break

    else:
        raise ValueError("Invalid card type specified. Use 'aadhar' or 'pan'.")

    return details

# Test the function
image_path = "pan_card.jpeg"  # Replace with the path to your image file
card_type = "pan"  # Change to "pan or aadhar" if testing with a PAN card or Aadhar card
card_details = extract_card_details(image_path, card_type=card_type)

print("Extracted Card Details:")
for key, value in card_details.items():
    print(f"{key}: {value}")
