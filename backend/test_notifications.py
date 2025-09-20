#!/usr/bin/env python3
"""
Test script to check notifications in the database.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.notification import Notification
from mongoengine import connect

def main():
    try:
        # Connect to database
        connect(host='mongodb://localhost:27017/truecred', alias='default')

        # Check existing notifications
        notifications = Notification.objects()
        print(f'Found {notifications.count()} notifications')

        for n in notifications:
            print(f'ID: {n.id}, User: {n.user_id}, Type: {n.type}, Title: {n.title}')
            print(f'Message: {n.message}')
            print(f'Created: {n.created_at}')
            print('---')

        # Test creating a notification
        print('Creating test notification...')
        test_notification = Notification.create_notification(
            user_id='test_user_123',
            notification_type='test',
            title='Test Notification',
            message='This is a test notification',
            data={'test': True}
        )

        if test_notification:
            print(f'Created notification: {test_notification.id}')
        else:
            print('Failed to create notification')

        # Check again
        notifications = Notification.objects()
        print(f'After creation: {notifications.count()} notifications')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()