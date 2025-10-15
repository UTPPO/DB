import logging, json
import azure.functions as func
def main(inputBlob: func.InputStream):
    logging.info(f"[BlobImporter] name={inputBlob.name} bytes={inputBlob.length}")
    try:
        obj = json.loads(inputBlob.read().decode("utf-8"))
        logging.info(f"[BlobImporter] type={type(obj).__name__}")
    except Exception as ex:
        logging.exception(f"parse error: {ex}")
        raise
