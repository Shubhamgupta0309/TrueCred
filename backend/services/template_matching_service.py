"""Template Matching Service for certificate verification."""
from typing import Dict, List, Optional, Tuple
from models.certificate_template import CertificateTemplate
from models.organization_profile import OrganizationProfile
from services.ocr_service import ocr_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateMatchingService:
    """Service for matching uploaded certificates against stored templates."""
    
    # Confidence thresholds
    THRESHOLD_AUTO_VERIFY = 50  # Auto-approve above this (>50)
    THRESHOLD_MANUAL_REVIEW = 30  # Manual review between 30-50
    THRESHOLD_REJECT = 30  # Auto-reject below this (<30)
    
    def __init__(self):
        """Initialize template matching service."""
        pass
    
    def process_and_store_template(
        self, 
        image_data: bytes,
        organization_id: str,
        organization_name: str,
        organization_type: str,
        template_name: str,
        template_type: str,
        file_url: str,
        file_hash: str,
        uploaded_by: str,
        required_fields: List[str] = None,
        optional_fields: List[str] = None
    ) -> Dict:
        """
        Process a new certificate template and store it.
        
        Args:
            image_data: Raw image bytes
            organization_id: Organization's unique ID
            organization_name: Organization name
            organization_type: 'college' or 'company'
            template_name: Name for this template
            template_type: Type of certificate (degree, internship, etc.)
            file_url: Storage URL (IPFS/cloud)
            file_hash: File integrity hash
            uploaded_by: User ID who uploaded
            required_fields: Required fields for verification
            optional_fields: Optional fields
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract text using OCR
            ocr_result = ocr_service.extract_text(image_data)
            
            if not ocr_result['success']:
                return {
                    'success': False,
                    'error': 'OCR processing failed',
                    'details': ocr_result.get('error')
                }
            
            # Extract key fields
            key_fields = ocr_service.extract_key_fields(ocr_result['full_text'])
            
            # Compute layout hash for quick matching
            layout_hash = ocr_service.compute_layout_hash(ocr_result['structured_data'])
            
            # Create template document
            template = CertificateTemplate(
                organization_id=organization_id,
                organization_name=organization_name,
                organization_type=organization_type,
                template_name=template_name,
                template_type=template_type,
                file_url=file_url,
                file_hash=file_hash,
                extracted_text=ocr_result['full_text'],
                key_fields=key_fields,
                template_features={
                    'total_words': ocr_result['total_words'],
                    'avg_confidence': ocr_result['average_confidence'],
                    'dimensions': ocr_result['image_dimensions']
                },
                layout_hash=layout_hash,
                uploaded_by=uploaded_by,
                required_fields=required_fields or [],
                optional_fields=optional_fields or []
            )
            
            template.save()
            
            logger.info(f"Template saved: {template_name} for {organization_name}")
            
            return {
                'success': True,
                'template_id': str(template.id),
                'extracted_text': ocr_result['full_text'][:500],  # Preview
                'key_fields': key_fields,
                'confidence': ocr_result['average_confidence']
            }
            
        except Exception as e:
            logger.error(f"Template processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_certificate_against_templates(
        self,
        image_data: bytes,
        organization_id: str,
        template_type: str = None,
        template_title: str = None
    ) -> Dict:
        """
        Verify an uploaded certificate against stored templates.
        
        Args:
            image_data: Raw certificate image bytes
            organization_id: Organization to match against
            template_type: Optional template type filter
            template_title: Optional request title to pre-filter templates by name
            
        Returns:
            Verification results with confidence score
        """
        try:
            # Extract text from uploaded certificate
            ocr_result = ocr_service.extract_text(image_data)
            
            if not ocr_result['success']:
                return {
                    'success': False,
                    'error': 'OCR processing failed',
                    'verification_status': 'failed'
                }
            
            # Get templates for this organization
            org_id_candidates = self._get_organization_id_candidates(organization_id)
            query = {
                'organization_id__in': org_id_candidates,
                'is_active': True
            }
            if template_type:
                query['template_type'] = template_type
            
            templates = CertificateTemplate.objects(**query)

            # Optional phase filter by request title/template name to avoid matching against unrelated templates.
            templates = self._filter_templates_by_title(templates, template_title)
            
            if not templates:
                title_msg = (
                    f" and title '{template_title}'"
                    if template_title else ""
                )
                return {
                    'success': False,
                    'error': f"No templates found for this organization IDs {org_id_candidates}{title_msg}",
                    'verification_status': 'no_template',
                    'confidence_score': 0
                }
            
            # Find best matching template
            best_match = self._find_best_template_match(
                ocr_result,
                templates
            )
            
            # Determine verification status based on confidence
            status = self._determine_verification_status(best_match['confidence_score'])
            decision_reason = self._build_decision_reason(
                best_match['confidence_score'],
                status,
                best_match.get('details', {})
            )
            
            # Update template statistics
            if best_match['template']:
                template = best_match['template']
                template.update_statistics(
                    best_match['confidence_score'],
                    status == 'verified'
                )
            
            return {
                'success': True,
                'verification_status': status,
                'confidence_score': best_match['confidence_score'],
                'matched_template_id': str(best_match['template'].id) if best_match['template'] else None,
                'matched_template_name': best_match['template'].template_name if best_match['template'] else None,
                'extracted_text': ocr_result['full_text'],
                'key_fields': ocr_service.extract_key_fields(ocr_result['full_text']),
                'matching_details': best_match['details'],
                'ocr_confidence': ocr_result['average_confidence'],
                'decision_reason': decision_reason,
                'template_title_filter': template_title,
                'thresholds': {
                    'auto_verify_above': self.THRESHOLD_AUTO_VERIFY,
                    'manual_review_min': self.THRESHOLD_MANUAL_REVIEW,
                    'reject_below': self.THRESHOLD_REJECT
                }
            }
            
        except Exception as e:
            logger.error(f"Certificate verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'verification_status': 'error'
            }
    
    def _find_best_template_match(
        self,
        ocr_result: Dict,
        templates: List[CertificateTemplate]
    ) -> Dict:
        """
        Find the best matching template from a list.
        
        Args:
            ocr_result: OCR extraction results
            templates: List of templates to match against
            
        Returns:
            Best match with confidence score
        """
        best_match = {
            'template': None,
            'confidence_score': 0,
            'details': {}
        }
        
        uploaded_text = ocr_result['full_text']
        uploaded_layout = ocr_service.compute_layout_hash(ocr_result['structured_data'])
        uploaded_key_fields = ocr_service.extract_key_fields(uploaded_text)
        
        for template in templates:
            # Calculate text similarity
            text_similarity = ocr_service.calculate_text_similarity(
                uploaded_text,
                template.extracted_text
            )
            
            # Calculate layout similarity
            layout_similarity = ocr_service.calculate_layout_similarity(
                uploaded_layout,
                template.layout_hash
            )
            
            # Combined confidence score (weighted average)
            # Text: 70%, Layout: 30%
            base_confidence = (text_similarity * 0.7) + (layout_similarity * 0.3)

            # Required-field adjustment:
            # if required fields are missing, confidence is reduced to avoid false positives.
            required_eval = self._evaluate_required_fields(
                template.required_fields or [],
                uploaded_key_fields
            )
            confidence_score = self._apply_required_field_adjustment(
                base_confidence,
                required_eval
            )
            
            if confidence_score > best_match['confidence_score']:
                best_match = {
                    'template': template,
                    'confidence_score': round(confidence_score, 2),
                    'details': {
                        'base_confidence': round(base_confidence, 2),
                        'text_similarity': round(text_similarity, 2),
                        'layout_similarity': round(layout_similarity, 2),
                        'template_avg_confidence': template.average_confidence,
                        'required_fields_total': required_eval['required_total'],
                        'required_fields_matched': required_eval['required_matched'],
                        'required_fields_missing': required_eval['missing_required_fields'],
                        'required_match_ratio': required_eval['required_match_ratio'],
                        'required_fields_penalty': required_eval['penalty'],
                        'uploaded_key_fields': sorted(list(uploaded_key_fields.keys()))
                    }
                }
        
        return best_match
    
    def _determine_verification_status(self, confidence_score: float) -> str:
        """
        Determine verification status based on confidence score.
        
        Args:
            confidence_score: Confidence score (0-100)
            
        Returns:
            Status string: 'verified' (>50), 'pending_review' (30-50), 'rejected' (<30)
        """
        if confidence_score > self.THRESHOLD_AUTO_VERIFY:  # >50: auto-approve
            return 'verified'
        elif confidence_score >= self.THRESHOLD_MANUAL_REVIEW:  # 30-50: manual review
            return 'pending_review'
        else:  # <30: direct reject
            return 'rejected'

    def _normalize_field_name(self, field_name: str) -> str:
        """Normalize field names to compare user-entered labels with OCR keys."""
        return (field_name or '').strip().lower().replace(' ', '_')

    def _normalize_title(self, title: str) -> str:
        """Normalize a title for resilient template-name matching."""
        return ''.join(ch for ch in (title or '').strip().lower() if ch.isalnum())

    def _title_matches(self, template_name: str, requested_title: str) -> bool:
        """Determine if a template name matches a requested title."""
        normalized_template = self._normalize_title(template_name)
        normalized_requested = self._normalize_title(requested_title)

        if not normalized_requested:
            return True

        if normalized_template == normalized_requested:
            return True

        # Allow strong partial match in either direction.
        return (
            normalized_requested in normalized_template or
            normalized_template in normalized_requested
        )

    def _filter_templates_by_title(self, templates: List[CertificateTemplate], template_title: str) -> List[CertificateTemplate]:
        """Filter templates by template_name when request title is provided."""
        if not template_title:
            return list(templates)

        filtered = [
            template for template in templates
            if self._title_matches(template.template_name, template_title)
        ]

        return filtered

    def _evaluate_required_fields(self, required_fields: List[str], uploaded_key_fields: Dict) -> Dict:
        """Evaluate required field coverage from OCR key extraction."""
        normalized_required = [self._normalize_field_name(name) for name in required_fields if name]
        normalized_required = [name for name in normalized_required if name]

        detected_keys = {
            self._normalize_field_name(key)
            for key in (uploaded_key_fields or {}).keys()
            if key
        }

        matched_required = [name for name in normalized_required if name in detected_keys]
        missing_required = [name for name in normalized_required if name not in detected_keys]

        required_total = len(normalized_required)
        required_matched = len(matched_required)
        required_match_ratio = round((required_matched / required_total) if required_total else 1.0, 2)

        # Penalty strategy keeps matching robust but explainable:
        # each missing required field reduces confidence by 8 points.
        penalty = float(len(missing_required) * 8)

        return {
            'required_total': required_total,
            'required_matched': required_matched,
            'missing_required_fields': missing_required,
            'required_match_ratio': required_match_ratio,
            'penalty': penalty
        }

    def _apply_required_field_adjustment(self, base_confidence: float, required_eval: Dict) -> float:
        """Apply required-field penalty to the base confidence score."""
        penalty = required_eval.get('penalty', 0.0)
        adjusted = max(0.0, base_confidence - penalty)
        return round(adjusted, 2)

    def _build_decision_reason(self, confidence_score: float, status: str, details: Dict) -> str:
        """Build a human-readable reason for the final verification status."""
        text_similarity = details.get('text_similarity', 0)
        layout_similarity = details.get('layout_similarity', 0)
        required_total = details.get('required_fields_total', 0)
        required_matched = details.get('required_fields_matched', 0)
        penalty = details.get('required_fields_penalty', 0)

        if status == 'verified':
            return (
                f"Auto-approved: final confidence {confidence_score}% (> {self.THRESHOLD_AUTO_VERIFY}). "
                f"Text similarity {text_similarity}%, layout similarity {layout_similarity}%, "
                f"required fields matched {required_matched}/{required_total}, penalty {penalty}."
            )
        if status == 'pending_review':
            return (
                f"Manual review: final confidence {confidence_score}% between "
                f"{self.THRESHOLD_MANUAL_REVIEW}-{self.THRESHOLD_AUTO_VERIFY}. "
                f"Text similarity {text_similarity}%, layout similarity {layout_similarity}%, "
                f"required fields matched {required_matched}/{required_total}, penalty {penalty}."
            )
        return (
            f"Rejected: final confidence {confidence_score}% (< {self.THRESHOLD_REJECT}). "
            f"Text similarity {text_similarity}%, layout similarity {layout_similarity}%, "
            f"required fields matched {required_matched}/{required_total}, penalty {penalty}."
        )

    def _get_organization_id_candidates(self, organization_id: str) -> List[str]:
        """Build equivalent organization identifiers (profile id and user id) for robust matching."""
        org_id = str(organization_id)
        candidates = {org_id}

        # If org_id is a profile id, include linked user id.
        profile_by_id = OrganizationProfile.objects(id=org_id).first()
        if profile_by_id and profile_by_id.user_id:
            candidates.add(str(profile_by_id.user_id))

        # If org_id is a user id, include linked profile id.
        profile_by_user = OrganizationProfile.objects(user_id=org_id).first()
        if profile_by_user:
            candidates.add(str(profile_by_user.id))

        return list(candidates)
    
    def get_templates_by_organization(
        self,
        organization_id: str,
        include_inactive: bool = False
    ) -> List[Dict]:
        """
        Get all templates for an organization.
        
        Args:
            organization_id: Organization ID
            include_inactive: Include inactive templates
            
        Returns:
            List of templates
        """
        query = {'organization_id__in': self._get_organization_id_candidates(organization_id)}
        if not include_inactive:
            query['is_active'] = True
        
        templates = CertificateTemplate.objects(**query)
        return [template.to_json() for template in templates]
    
    def deactivate_template(self, template_id: str) -> bool:
        """
        Deactivate a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Success status
        """
        try:
            template = CertificateTemplate.objects(id=template_id).first()
            if template:
                template.is_active = False
                template.updated_at = datetime.utcnow()
                template.save()
                return True
            return False
        except Exception as e:
            logger.error(f"Template deactivation failed: {str(e)}")
            return False


# Singleton instance
template_matching_service = TemplateMatchingService()
