# 🚀 Quick Start - OCR Certificate Verification

## ⚡ 5-Minute Setup

### Step 1: Install Tesseract (Windows)

```powershell
# Download and run installer
# https://github.com/UB-Mannheim/tesseract/wiki
# Select: tesseract-ocr-w64-setup-5.3.3.exe
# Install to default: C:\Program Files\Tesseract-OCR\

# Verify installation
tesseract --version
```

### Step 2: Install Python Dependencies

```powershell
cd backend
pip install pytesseract Pillow opencv-python scikit-image numpy
```

### Step 3: Start Backend

```powershell
cd backend
python app.py
```

### Step 4: Start Frontend

```powershell
cd frontend
npm install   # if first time
npm run dev
```

## ✅ Quick Test

### Upload a Template (as College):

1. Login as college admin
2. Go to "Certificate Templates" tab
3. Click "Upload New Template"
4. Upload any certificate image
5. Fill template name and type
6. Click "Upload Template"

### Verify a Certificate (as Student):

1. Login as student
2. Navigate to verification page
3. Select organization
4. Upload certificate (same or similar to template)
5. Click "Verify Certificate"
6. See confidence score and status!

## 🎯 Expected Results

### Good Template:

- OCR Confidence: 70-95%
- Extracted text visible
- Key fields identified (name, date, etc.)

### Successful Verification:

- Confidence Score: 80-95%
- Status: ✅ Verified (green)
- Matched Template shown
- Extracted data displayed

### Manual Review Needed:

- Confidence Score: 60-79%
- Status: ⚠️ Pending Review (yellow)
- Requires admin approval

## 🐛 Troubleshooting

**"Tesseract not found"**
→ Add to PATH: `C:\Program Files\Tesseract-OCR`

**"Low confidence scores"**
→ Use high-quality images (min 1500px width)

**"No templates found"**
→ Ensure organization ID matches template

## 📊 What to See

### In Database (MongoDB):

```javascript
// certificate_templates collection
{
  template_name: "Computer Science Degree",
  total_verifications: 5,
  average_confidence: 87,
  is_active: true
}

// credential_requests collection
{
  confidence_score: 87,
  verification_status: "verified",
  matched_template_name: "Computer Science Degree"
}
```

### In UI:

- College Dashboard → "Certificate Templates" tab
- Upload form with drag-drop
- Templates grid with statistics
- Verification component with progress bar

## 🎉 Success Indicators

✅ Tesseract version displays  
✅ Backend starts without errors  
✅ Frontend shows templates tab  
✅ Template uploads successfully  
✅ OCR extracts text from image  
✅ Verification returns confidence score  
✅ Statistics update after verification

---

**📚 Full documentation:** See `OCR_SETUP_GUIDE.md`  
**🔧 Implementation details:** See `OCR_IMPLEMENTATION.md`
