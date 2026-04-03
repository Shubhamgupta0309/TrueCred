"""OCR Service for extracting text from certificates using Tesseract."""
import io
import os
import hashlib
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    OCR_IMPORT_ERROR = None
except ImportError as exc:
    pytesseract = None
    Image = Any
    cv2 = None
    np = None
    OCR_IMPORT_ERROR = exc

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None


class OCRService:
    """Service for OCR processing and text extraction from certificates."""
    
    def __init__(self):
        """Initialize OCR service with Tesseract configuration."""
        self.available = OCR_IMPORT_ERROR is None

        # Set Tesseract path for Windows (update if installed elsewhere)
        if self.available and os.name == 'nt':  # Windows
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # OCR configuration for better accuracy
        self.config = '--oem 3 --psm 6'  # LSTM + Assume uniform block of text

    def _ensure_dependencies(self) -> None:
        """Raise a clear error if OCR dependencies are unavailable."""
        if not self.available:
            raise RuntimeError(
                'OCR dependencies are not installed. Run "pip install -r requirements.txt" '
                'or install pytesseract, Pillow, opencv-python, scikit-image, and numpy.'
            ) from OCR_IMPORT_ERROR
    
    def preprocess_image(self, image: Image.Image):
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image as numpy array
        """
        self._ensure_dependencies()

        # Convert PIL to OpenCV format
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Resize if too small (minimum 1000px width for better OCR)
        height, width = gray.shape
        if width < 1000:
            scale = 1000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding for better contrast
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Dilate to connect broken characters
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        return dilated
    
    def extract_text(self, image_path_or_bytes) -> Dict:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_path_or_bytes: File path or bytes of image
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            self._ensure_dependencies()

            # Load image
            if isinstance(image_path_or_bytes, bytes):
                image = self._load_image_from_bytes(image_path_or_bytes)
            else:
                image = self._load_image_from_path(image_path_or_bytes)
            
            # Preprocess
            processed_img = self.preprocess_image(image)
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(
                processed_img, 
                config=self.config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Extract full text
            full_text = pytesseract.image_to_string(processed_img, config=self.config)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract structured data (words with positions)
            structured_data = []
            for i, text in enumerate(data['text']):
                if text.strip():  # Skip empty strings
                    structured_data.append({
                        'text': text,
                        'confidence': int(data['conf'][i]),
                        'left': int(data['left'][i]),
                        'top': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i])
                    })
            
            return {
                'success': True,
                'full_text': full_text.strip(),
                'structured_data': structured_data,
                'average_confidence': round(avg_confidence, 2),
                'total_words': len([t for t in data['text'] if t.strip()]),
                'image_dimensions': {
                    'width': image.width,
                    'height': image.height
                }
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'structured_data': [],
                'average_confidence': 0
            }

    def _load_image_from_bytes(self, file_bytes: bytes):
        """Load an image from bytes and render first page for PDFs."""
        if file_bytes.startswith(b'%PDF'):
            if pdfium is None:
                raise RuntimeError(
                    'PDF OCR requires pypdfium2. Install it with "pip install pypdfium2".'
                )
            return self._render_pdf_first_page(file_bytes)
        return Image.open(io.BytesIO(file_bytes))

    def _load_image_from_path(self, file_path: str):
        """Load an image from path and render first page for PDFs."""
        if str(file_path).lower().endswith('.pdf'):
            if pdfium is None:
                raise RuntimeError(
                    'PDF OCR requires pypdfium2. Install it with "pip install pypdfium2".'
                )
            with open(file_path, 'rb') as f:
                return self._render_pdf_first_page(f.read())
        return Image.open(file_path)

    def _render_pdf_first_page(self, file_bytes: bytes):
        """Render first PDF page to PIL image for OCR."""
        pdf = pdfium.PdfDocument(file_bytes)
        if len(pdf) == 0:
            raise RuntimeError('PDF has no pages for OCR.')

        page = pdf[0]
        # Render at 2x scale for improved OCR readability.
        bitmap = page.render(scale=2)
        pil_image = bitmap.to_pil()
        page.close()
        pdf.close()
        return pil_image
    
    def extract_key_fields(self, text: str) -> Dict:
        """
        Extract common certificate fields from text.
        
        Args:
            text: Extracted text from certificate
            
        Returns:
            Dictionary of identified fields
        """
        key_fields = {}
        lines = text.split('\n')
        
        # Common patterns for certificate fields
        patterns = {
            'name': ['name:', 'student name:', 'candidate:', 'awarded to'],
            'course': ['course:', 'program:', 'degree:', 'certification in'],
            'date': ['date:', 'issued on:', 'completed on:', 'awarded on'],
            'grade': ['grade:', 'cgpa:', 'percentage:', 'marks:'],
            'roll_number': ['roll no:', 'enrollment no:', 'registration no:'],
            'certificate_number': ['certificate no:', 'cert no:', 'certificate id:']
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            for field, keywords in patterns.items():
                for keyword in keywords:
                    if keyword in line_lower:
                        # Extract value after keyword
                        value = line.split(':', 1)[-1].strip()
                        if value:
                            key_fields[field] = value
                        break
        
        return key_fields
    
    def compute_layout_hash(self, structured_data: list) -> str:
        """
        Compute a hash representing the layout structure.
        Used for quick template matching.
        
        Args:
            structured_data: List of words with positions
            
        Returns:
            Hash string representing layout
        """
        # Create a simplified representation of layout
        layout_str = ""
        for item in structured_data:
            # Normalize position (relative to image size)
            layout_str += f"{item['left']//50}_{item['top']//50}_"
        
        # Return hash
        return hashlib.md5(layout_str.encode()).hexdigest()
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts (0-100%).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity percentage
        """
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return round((intersection / union) * 100, 2)
    
    def calculate_layout_similarity(self, layout1: str, layout2: str) -> float:
        """
        Calculate similarity between two layout hashes.
        
        Args:
            layout1: First layout hash
            layout2: Second layout hash
            
        Returns:
            Similarity percentage
        """
        # Simple character matching
        if not layout1 or not layout2:
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(layout1, layout2))
        return round((matches / len(layout1)) * 100, 2)


# Singleton instance
ocr_service = OCRService()
