"""
Minimal company review endpoints to support the frontend's pending/history and approve/reject flows.

These are additive, scoped routes that don't disturb the existing Experiences API.
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist

from models.experience import Experience
from models.user import User

company_exp_bp = Blueprint('experiences_company', __name__, url_prefix='/api/experiences')


def _format_date(dt):
    try:
        return dt.strftime('%b %d, %Y') if dt else None
    except Exception:
        return None


@company_exp_bp.route('/pending', methods=['GET'])
@jwt_required()
def pending_experiences():
    # For now, return globally pending experiences
    exps = Experience.objects(verification_status='pending').order_by('-created_at')
    out = []
    for x in exps:
        try:
            student = x.user
            out.append({
                'id': str(x.id),
                'studentName': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                'experienceTitle': x.title,
                'company': x.organization,
                'duration': None,
                'submissionDate': _format_date(x.created_at) or _format_date(x.updated_at) or _format_date(datetime.utcnow()),
            })
        except Exception:
            out.append({
                'id': str(x.id),
                'studentName': 'Student',
                'experienceTitle': x.title,
                'company': x.organization,
                'duration': None,
                'submissionDate': _format_date(x.created_at) or _format_date(datetime.utcnow()),
            })
    return jsonify({'requests': out}), 200


@company_exp_bp.route('/history', methods=['GET'])
@jwt_required()
def experiences_history():
    exps = Experience.objects(verification_status__in=['verified', 'rejected']).order_by('-updated_at')
    out = []
    for x in exps:
        try:
            student = x.user
            out.append({
                'id': str(x.id),
                'studentName': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                'experienceTitle': x.title,
                'status': 'verified' if x.is_verified else 'rejected',
                'actionDate': _format_date(x.updated_at) or _format_date(datetime.utcnow()),
            })
        except Exception:
            out.append({
                'id': str(x.id),
                'studentName': 'Student',
                'experienceTitle': x.title,
                'status': 'verified' if x.is_verified else 'rejected',
                'actionDate': _format_date(x.updated_at) or _format_date(datetime.utcnow()),
            })
    return jsonify({'history': out}), 200


@company_exp_bp.route('/request', methods=['POST'])
@jwt_required()
def request_experience_verification():
    """Create an experience verification request from minimal input."""
    data = request.json or {}
    title = data.get('title') or data.get('experienceTitle')
    company = data.get('company') or data.get('organization')
    if not title or not company:
        return jsonify({'error': 'Missing field: title or company'}), 400

    # Build a minimal Experience record
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        return jsonify({'error': 'User not found'}), 404

    exp = Experience(
        user=user,
        title=title,
        organization=company,
        type=data.get('type', 'work'),
        start_date=datetime.utcnow(),
        description=data.get('description'),
        is_current=True,
        pending_verification=True,
        verification_status='pending',
        metadata=data.get('metadata') or {},
    )
    exp.save()
    return jsonify({'success': True, 'id': str(exp.id)}), 201


@company_exp_bp.route('/<experience_id>/approve', methods=['POST'])
@jwt_required()
def approve_experience(experience_id):
    try:
        exp = Experience.objects.get(id=experience_id)
    except DoesNotExist:
        return jsonify({'error': 'Experience not found'}), 404
    # Update fields to mark verified
    exp.is_verified = True
    exp.verification_status = 'verified'
    exp.rejection_reason = None
    exp.pending_verification = False
    exp.verified_at = datetime.utcnow()
    exp.save()
    return jsonify({'success': True}), 200


@company_exp_bp.route('/<experience_id>/reject', methods=['POST'])
@jwt_required()
def reject_experience(experience_id):
    try:
        exp = Experience.objects.get(id=experience_id)
    except DoesNotExist:
        return jsonify({'error': 'Experience not found'}), 404
    reason = (request.json or {}).get('reason')
    exp.is_verified = False
    exp.verification_status = 'rejected'
    exp.rejection_reason = reason
    exp.pending_verification = False
    exp.save()
    return jsonify({'success': True}), 200
