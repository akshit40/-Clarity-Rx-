import PIL.Image
import PIL.ImageEnhance
import PIL.ImageFilter
from src.utils import setup_logger

logger = setup_logger(__name__)

class ImageProcessor:
    """
    Advanced Image Processing for Medical Prescription Extraction.
    Handles blurring and low contrast.
    """
    @staticmethod
    def process_for_ocr(image_path):
        """
        Enhances the image for better OCR accuracy.
        """
        try:
            logger.info(f"Processing image for OCR enhancement: {image_path}")
            img = PIL.Image.open(image_path)
            
            # 1. Convert to Grayscale (removes distracting colors)
            img = img.convert('L')
            
            # 2. Enhance Contrast (makes text stand out)
            enhancer = PIL.ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0) # Double the contrast
            
            # 3. Enhance Sharpness (targets blurry handwriting)
            enhancer = PIL.ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.5) # Significant sharpening
            
            # 4. Adaptive Brightness
            enhancer = PIL.ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)

            # 5. Optional Filter (Unsharp Mask equivalent)
            img = img.filter(PIL.ImageFilter.SHARPEN)
            
            # Save a debug copy (optional, can be disabled)
            processed_path = image_path.replace(".", "_processed.")
            img.save(processed_path)
            
            return img
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return PIL.Image.open(image_path) # Fallback to original
