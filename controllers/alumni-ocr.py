import sys
import json
import cv2
import numpy as np
from PIL import Image, ExifTags
import pytesseract
import re
from dotenv import load_dotenv
import os

load_dotenv()
tesseract_path = os.getenv("TESSERACT_PATH")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def fix_image_orientation(pil_img):
    try:
        exif = pil_img._getexif()
        if exif:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            orientation_value = exif.get(orientation, None)
            print("EXIF orientation:", orientation_value, file=sys.stderr)

            if orientation_value == 3:
                pil_img = pil_img.rotate(180, expand=True)
            elif orientation_value == 6:
                pil_img = pil_img.rotate(270, expand=True)
            elif orientation_value == 8:
                pil_img = pil_img.rotate(90, expand=True)
        else:
            print("⚠️ No EXIF found in image.", file=sys.stderr)
    except Exception as e:
        print("EXIF rotation error:", str(e), file=sys.stderr)

    return pil_img

def clean_name(name_line):
    # Remove anything that's not a letter
    name_line = re.sub(r'[^a-zA-Z]', '', name_line)
    # Insert spaces before uppercase letters (if needed)
    spaced = re.sub(r'(?<!^)([A-Z])', r' \1', name_line)
    return spaced.strip()

def extract_data(image_path):
    image = Image.open(image_path)
    # image = image.rotate(90, expand=True)  # adjust as needed

    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Preprocessing
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(thresh, 3)

    # Full OCR (no whitelist so we can detect roll number)
    full_text = pytesseract.image_to_string(
        denoised,
        config='--oem 3 --psm 4'
    )
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]

    # Extract name (first alphabetic line)
    text_alpha = pytesseract.image_to_string(
        denoised,
        config='--oem 3 --psm 4 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    )

    # print("=== RAW OCR TEXT ===")
    # print(text_alpha)


    alpha_lines = [line.strip() for line in text_alpha.split('\n') if line.strip()]

    # extract name
    # little erorr adds ig to the start of name trying to find the cause
    name = "Not found"
    for i, line in enumerate(alpha_lines):
        if 'Name' in line and i + 1 < len(alpha_lines):
            name = clean_name(alpha_lines[i + 1])
            break
        elif len(line.split()) >= 2 and re.match(r'^[A-Za-z\s]+$', line):
            name = clean_name(line)
            break


    # Extract roll number
    roll_match = re.search(r'\d{4}-\d{2}-\d{4}', full_text)
    roll_number = roll_match.group() if roll_match else "Not found"

    return {'name': name, 'roll_number': roll_number}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(json.dumps({"error": "File not found"}))
        sys.exit(1)

    try:
        result = extract_data(image_path)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
