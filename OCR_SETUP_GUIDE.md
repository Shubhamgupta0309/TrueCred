# OCR Certificate Verification - Installation & Setup Guide

## 🎯 Overview

This guide will help you set up the Tesseract OCR-based certificate verification system for TrueCred. The system enables automatic verification of certificates by comparing uploaded certificates against stored templates using OCR technology.

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB running
- Tesseract OCR installed

## 🔧 Installation Steps

### Step 1: Install Tesseract OCR

#### Windows:

1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (recommended: `tesseract-ocr-w64-setup-5.3.3.exe`)
3. **Important:** During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR\`)
4. Add Tesseract to PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - Add: `C:\Program Files\Tesseract-OCR`
5. Verify installation:
   ```powershell
   tesseract --version
   ```

#### Linux:

```bash
sudo apt update
sudo apt install tesseract-ocr
```

#### macOS:

```bash
brew install tesseract
```

### Step 2: Install Python Dependencies

Navigate to the backend directory and install:

```powershell
cd backend
pip install -r requirements.txt
```

New packages installed:

- `pytesseract==0.3.10` - Python wrapper for Tesseract
- `Pillow==10.0.0` - Image processing
- `opencv-python==4.8.0.74` - Computer vision
- `scikit-image==0.21.0` - Image analysis
- `numpy==1.24.3` - Numerical computing

### Step 3: Verify OCR Service

Test if Tesseract is properly configured:

```python
# Run this in Python console
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print("Tesseract configured successfully!")
```

### Step 4: Database Migration

The new models will be automatically created by MongoEngine when first accessed. No manual migration needed!

New collections added:

- `certificate_templates` - Stores organization certificate templates
- Updated `credential_requests` - Now includes OCR verification fields

### Step 5: Start Backend Server

```powershell
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### Step 6: Install Frontend Dependencies

```powershell
cd frontend
npm install
```

### Step 7: Start Frontend

```powershell
npm run dev
```

The frontend will start on `http://localhost:5173`

## 🚀 Usage Guide

### For Colleges/Organizations:

#### 1. Upload Certificate Templates

1. Log in to your College Dashboard
2. Navigate to **"Certificate Templates"** tab
3. Click **"Upload New Template"**
4. Fill in the form:
   - **Template File:** Upload a master certificate (PNG/JPG)
   - **Template Name:** E.g., "Computer Science Degree 2024"
   - **Certificate Type:** Select from dropdown
   - **Required Fields:** Comma-separated (e.g., `name, date, course`)
   - **Optional Fields:** Additional fields (e.g., `grade, roll_number`)
5. Click **"Upload Template"**

The system will:

- Extract text using OCR
- Identify key fields
- Calculate layout hash
- Store for future comparisons

#### 2. Manage Templates

- View all uploaded templates
- See verification statistics
- Deactivate outdated templates
- Monitor success rates and confidence scores

### For Students:

#### 1. Upload Certificate for Verification

1. Navigate to upload section
2. Select your organization
3. Upload your certificate image
4. (Optional) Select certificate type
5. Click **"Verify Certificate"**

#### 2. View Results

The system will show:

- **Verification Status:**
  - ✅ **Verified** (85%+ confidence) - Auto-approved
  - ⚠️ **Pending Review** (60-84% confidence) - Manual review required
  - ❌ **Rejected** (<60% confidence) - Does not match templates
- **Confidence Score** (0-100%)
- **Matched Template**
- **Extracted Data** (name, date, course, etc.)
- **Matching Details** (text/layout similarity)

## 📊 API Endpoints

### Template Management

#### Upload Template

```http
POST /api/templates/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body (FormData):
- template_file: File
- template_name: String
- template_type: String
- organization_id: String
- organization_name: String
- organization_type: String ('college' or 'company')
- required_fields: JSON array
- optional_fields: JSON array
```

#### Get Organization Templates

```http
GET /api/templates/organization/{organization_id}
Authorization: Bearer <token>
```

#### Get Template Statistics

```http
GET /api/templates/{template_id}/statistics
Authorization: Bearer <token>
```

#### Deactivate Template

```http
POST /api/templates/{template_id}/deactivate
Authorization: Bearer <token>
```

### OCR Verification

#### Verify Certificate

```http
POST /api/ocr/verify-credential-ocr
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body (FormData):
- credential_file: File
- organization_id: String
- template_type: String (optional)
- credential_request_id: String (optional)
```

Response:

```json
{
  "success": true,
  "data": {
    "verification_status": "verified",
    "confidence_score": 87,
    "matched_template": "Computer Science Degree 2024",
    "extracted_data": {
      "name": "John Doe",
      "course": "Computer Science",
      "date": "June 2024"
    },
    "matching_details": {
      "text_similarity": 89.5,
      "layout_similarity": 84.2
    },
    "message": "Certificate verified successfully! High confidence match."
  }
}
```

## 🎨 Frontend Components

### New Components:

1. **TemplateUpload.jsx**
   - Upload certificate templates
   - Preview uploaded images
   - Configure required/optional fields
   - View OCR extraction results

2. **TemplateManager.jsx**
   - List all templates
   - View template statistics
   - Manage template lifecycle
   - Deactivate old templates

3. **OCRVerification.jsx**
   - Upload certificates for verification
   - Visual confidence score display
   - Show extracted data
   - Display matching details

### Integration:

Updated **CollegeDashboard.jsx**:

- Added "Certificate Templates" tab
- Integrated TemplateManager component

## 🔍 How It Works

### Template Upload Process:

1. Organization uploads master certificate
2. **Image Preprocessing:**
   - Convert to grayscale
   - Resize to minimum 1000px width
   - Apply denoising
   - Adaptive thresholding
   - Character dilation
3. **OCR Extraction:**
   - Extract full text with Tesseract
   - Identify word positions
   - Calculate confidence scores
4. **Feature Extraction:**
   - Extract key fields (name, date, etc.)
   - Compute layout hash
   - Store template features
5. **Save to Database**

### Verification Process:

1. Student uploads certificate
2. **OCR Processing:**
   - Same preprocessing as template
   - Extract text and layout
3. **Template Matching:**
   - Find templates for organization
   - Calculate text similarity (70% weight)
   - Calculate layout similarity (30% weight)
   - Combined confidence score
4. **Decision Making:**
   - ≥85%: Auto-verify
   - 60-84%: Manual review
   - <60%: Reject
5. **Update Statistics**

## 🔧 Troubleshooting

### Tesseract Not Found Error:

**Error:** `TesseractNotFoundError`

**Solution:**

1. Verify Tesseract installation:
   ```powershell
   tesseract --version
   ```
2. Update path in `backend/services/ocr_service.py`:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'YOUR_TESSERACT_PATH\tesseract.exe'
   ```

### Low OCR Accuracy:

**Issue:** OCR confidence < 50%

**Solutions:**

- Ensure certificates are high resolution (min 1000px width)
- Check image quality (avoid blurry/distorted images)
- Use clear fonts in certificates
- Avoid handwritten text
- Ensure good lighting in scans

### Template Not Matching:

**Issue:** No templates found or low confidence

**Solutions:**

- Verify organization ID is correct
- Ensure template type matches (if specified)
- Check if template is active
- Upload multiple template variations
- Review extracted text for accuracy

### File Upload Error:

**Error:** "Failed to upload to IPFS"

**Solution:**

- Ensure IPFS service is running
- Check IPFS configuration in backend
- Verify file size < 10MB
- Check file format (PNG/JPG only)

## 📈 Performance Optimization

### For Better Accuracy:

1. **Template Quality:**
   - Use high-resolution templates (min 1500px)
   - Clear, consistent fonts
   - Good contrast (dark text, light background)

2. **Multiple Templates:**
   - Upload different certificate designs
   - Cover all degree programs
   - Update yearly templates

3. **Field Configuration:**
   - Define clear required fields
   - Use consistent field names
   - Add optional fields for better matching

### For Speed:

1. **Image Optimization:**
   - Compress images before upload
   - Max 2-3MB per image
   - PNG/JPG only (no PDF for verification)

2. **Caching:**
   - Templates cached in memory
   - Layout hashes for quick lookup
   - Reuse OCR results

## 🔒 Security Considerations

1. **File Validation:**
   - Only PNG/JPG files accepted
   - Max 10MB file size
   - Malware scanning recommended (not included)

2. **Access Control:**
   - JWT authentication required
   - Organization verification enforced
   - Template ownership verified

3. **Data Privacy:**
   - Extracted text stored securely
   - IPFS for distributed storage
   - No third-party API calls (fully local)

## 📊 Monitoring & Analytics

### Template Performance:

Track these metrics per template:

- Total verifications attempted
- Successful matches count
- Average confidence score
- Success rate percentage

### System Health:

Monitor:

- OCR processing time (should be 1-3s)
- Template matching speed
- Database query performance
- IPFS upload success rate

## 🚀 Next Steps

1. **Test the System:**
   - Upload 2-3 test templates
   - Try verifying certificates
   - Check confidence scores

2. **Optimize Templates:**
   - Add production templates
   - Configure field requirements
   - Test with real certificates

3. **Train Users:**
   - Guide colleges on template upload
   - Help students use verification
   - Provide support for edge cases

4. **Monitor & Improve:**
   - Review verification statistics
   - Adjust confidence thresholds if needed
   - Update templates regularly

## ❓ FAQ

**Q: Can I use PDF certificates?**
A: For templates, yes. For verification, convert to image first for best accuracy.

**Q: How accurate is the OCR?**
A: Tesseract achieves 85-92% on clean certificates. Google Vision (paid) offers 94-98%.

**Q: Can I verify handwritten certificates?**
A: Limited accuracy. Printed text works best. Handwritten requires Google Vision API.

**Q: How many templates should I upload?**
A: At least one per certificate type. More variations improve matching accuracy.

**Q: What if confidence is always low?**
A: Check template quality, ensure certificate format matches, adjust preprocessing settings.

## 📞 Support

For issues or questions:

1. Check troubleshooting section above
2. Review backend logs: `backend/logs/`
3. Test OCR independently with sample images
4. Verify all dependencies installed correctly

---

**🎉 Congratulations!** Your OCR verification system is now ready to use!
