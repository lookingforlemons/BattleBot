# DEVELOPMENT ONLY

from PIL import Image
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

text = pytesseract.image_to_string(Image.open('images/test.png'))

for line in text.splitlines(True):
    words = line.split(" ")
    for word in words:
        print(word)
        no_comma = word.replace(",", "")
        no_comma_no_period = no_comma.replace(".", "")
        d=l=0
        for c in no_comma_no_period:
            if c.isdigit():
                d=d+1
            elif c.isalpha():
                l=l+1
            else:
                pass

        if d >= 6:
            if d <= 8:
                if "/" in no_comma_no_period:
                    continue
                if "x" in no_comma_no_period:
                    continue
                if "%" in no_comma_no_period:
                    continue
                player_score = no_comma_no_period
        else:
            pass

print(player_score)