"""
Tests for education validation and user profile completion logic.

These tests exercise the `Education.clean()` and `User.clean()` methods
without requiring a running MongoDB instance (they only call validation
methods and inspect in-memory state).
"""
import pytest

from mongoengine.errors import ValidationError

from models.user import Education, User


def test_education_clean_requires_fields():
    # Missing required fields should raise ValidationError
    edu = Education(
        institution='  ',
        degree='',
        field_of_study=None,
        start_date=''
    )

    with pytest.raises(ValidationError):
        edu.clean()


def test_user_profile_completed_set_when_education_present():
    # Create a valid Education and attach to User; calling clean() should
    # set profile_completed to True
    edu = Education(
        institution='Example University',
        degree='B.Sc. Computer Science',
        field_of_study='Computer Science',
        start_date='2019-08-01',
        end_date='2022-05-30',
        current=False
    )

    user = User(
        username='teststudent',
        email='student@example.com',
        password='irrelevant123',
    )

    # Attach education as a list of embedded documents
    user.education = [edu]

    # Before cleaning, profile_completed may be default False
    assert not getattr(user, 'profile_completed', False) is True

    # Running clean should validate embedded docs and set profile_completed
    user.clean()

    assert user.profile_completed is True
