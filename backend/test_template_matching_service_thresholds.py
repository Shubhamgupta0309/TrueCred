from services.template_matching_service import TemplateMatchingService


def test_threshold_status_mapping():
    service = TemplateMatchingService()

    assert service._determine_verification_status(51) == 'verified'
    assert service._determine_verification_status(50) == 'pending_review'
    assert service._determine_verification_status(30) == 'pending_review'
    assert service._determine_verification_status(29.99) == 'rejected'


def test_required_field_evaluation_and_penalty():
    service = TemplateMatchingService()

    required_fields = ['name', 'course', 'certificate number']
    uploaded_key_fields = {
        'name': 'Test User',
        'course': 'B.Tech'
    }

    result = service._evaluate_required_fields(required_fields, uploaded_key_fields)

    assert result['required_total'] == 3
    assert result['required_matched'] == 2
    assert 'certificate_number' in result['missing_required_fields']
    assert result['penalty'] == 8.0

    adjusted = service._apply_required_field_adjustment(52.0, result)
    assert adjusted == 44.0
    assert service._determine_verification_status(adjusted) == 'pending_review'


def test_decision_reason_contains_breakdown():
    service = TemplateMatchingService()
    details = {
        'text_similarity': 64.0,
        'layout_similarity': 41.0,
        'required_fields_total': 3,
        'required_fields_matched': 2,
        'required_fields_penalty': 8.0,
    }

    reason = service._build_decision_reason(44.0, 'pending_review', details)

    assert 'Manual review' in reason
    assert '44.0%' in reason
    assert 'required fields matched 2/3' in reason


def test_template_title_matching_exact_and_partial():
    service = TemplateMatchingService()

    assert service._title_matches('Employee of the Month', 'Employee of the Month') is True
    assert service._title_matches('Employee of the Month - March 2026', 'Employee of the Month') is True
    assert service._title_matches('Employee of the Month', 'Employee of the Month March') is True


def test_template_title_matching_negative_case():
    service = TemplateMatchingService()

    assert service._title_matches('Degree Certificate', 'Employee of the Month') is False
