
import os
import io
import json
import logging
import gzip
from pathlib import Path

from pdf2image import convert_from_path
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse

vision_client = vision.ImageAnnotatorClient()


def google_ocr(image, lang_hint=None):
    if isinstance(image, (str, Path)):
        with io.open(image, "rb") as image_file:
            content = image_file.read()
    else:
        content = image
    ocr_image = vision.Image(content=content)

    features = [
        {
            "type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION,
            "model": "builtin/weekly",
        }
    ]
    image_context = {}
    if lang_hint:
        image_context["language_hints"] = [lang_hint]

    response = vision_client.annotate_image(
        {"image": ocr_image, "features": features, "image_context": image_context}
    )
    response_json = AnnotateImageResponse.to_json(response)
    response = json.loads(response_json)
    return response


def gzip_str(string_):
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())
    bytes_obj = out.getvalue()
    return bytes_obj


def apply_ocr_on_folder(images_dir, OCR_dir, lang=None):
    if not images_dir.is_dir():
        return
    for img_fn in images_dir.iterdir():
        result_fn = OCR_dir / f"{img_fn.stem}.json.gz"
        if result_fn.is_file():
            continue
        try:
            result = google_ocr(str(img_fn), lang_hint=lang)
        except:
            logging.exception(f"Google OCR issue: {result_fn}")
            continue
        result = json.dumps(result)
        gzip_result = gzip_str(result)
        result_fn.write_bytes(gzip_result)


def pdf_to_images(pdf_path, images_path):
    pages = convert_from_path(pdf_path)
    for i, page in enumerate(pages, 1):
        page.save(os.path.join(images_path, f"page_{i:06}.jpg"), "JPEG")


def ocr_pdf(pdf_path):
    images_path = Path(f"./data/images/{pdf_path.stem}/")
    OCR_output_path = Path(f"./data/OCR/{pdf_path.stem}/")
    images_path.mkdir(parents=True, exist_ok=True)
    OCR_output_path.mkdir(parents=True, exist_ok=True)
    pdf_to_images(pdf_path, images_path)
    apply_ocr_on_folder(
            images_dir = images_path,
            OCR_dir = OCR_output_path
        )
    
def ocr_images(images_path):
    OCR_output_path = Path(f"./data/OCR/{images_path.stem}/")
    apply_ocr_on_folder(
            images_dir = images_path,
            OCR_dir = OCR_output_path
        )
    
if __name__ == "__main__":
    # pdf_path = Path("./data/pdf/གཙུག་གཅེས་6.pdf")
    # ocr_pdf(pdf_path)
    images_path = Path("./data/images/ཁྱེད་རང་རྒྱལ་ཐུབ།")
    ocr_images(images_path)