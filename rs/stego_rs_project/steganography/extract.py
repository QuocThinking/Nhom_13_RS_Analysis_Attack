from PIL import Image

def _binary_to_text(binary_data: str) -> str:
    """Chuyển chuỗi nhị phân thành text"""
    chars = []
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8:
            continue
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def extract_text(stego_image_path: str) -> str:
    """Giải mã text đã giấu trong ảnh"""
    img = Image.open(stego_image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = img.load()

    width, height = img.size
    binary_data = ""

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for color in (r, g, b):
                binary_data += str(color & 1)

                if binary_data.endswith("1111111111111110"):
                    binary_data = binary_data[:-16]
                    text = _binary_to_text(binary_data)
                    print("DEBUG Extracted:", text)   # ✅ in ra terminal
                    return text
    text = _binary_to_text(binary_data)
    print("DEBUG Extracted (no delimiter):", text)
    return text
