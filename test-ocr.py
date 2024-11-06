import easyocr

# Initialize the reader. You can specify the languages you want to recognize.
reader = easyocr.Reader(['en'])

# Path to your image file
image_path = 'D:\kustodian\OCR\harsh_aadhar.jpg'

# Use the reader to read the text from the image
results = reader.readtext(image_path)


# Print the results
for result in results:
    print("Detected text:", result[1])
    print("Bounding box coordinates:", result[0])
    print("Confidence score:", result[2])