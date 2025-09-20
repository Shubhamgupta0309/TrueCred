from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from utils.jwt_helpers import decode_token
import json
from datetime import datetime

socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

class WebSocketService:
    def __init__(self):
        self.connected_users = {}  # user_id -> sid mapping
        self.user_rooms = {}  # user_id -> list of rooms

    def init_app(self, app):
        socketio.init_app(app, cors_allowed_origins="*")

    def emit_to_user(self, user_id, event, data):
        """Emit event to specific user"""
        if user_id in self.connected_users:
            sid = self.connected_users[user_id]
            emit(event, data, room=sid)
            return True
        return False

    def emit_to_room(self, room, event, data):
        """Emit event to all users in a room"""
        emit(event, room=room)

    def emit_notification(self, user_id, notification_data):
        """Emit notification to user"""
        success = self.emit_to_user(user_id, 'notification', notification_data)
        if success:
            print(f"Real-time notification sent to user {user_id}")
        return success

    def emit_experience_update(self, user_id, experience_data):
        """Emit experience update to user"""
        self.emit_to_user(user_id, 'experience_update', experience_data)

    def emit_credential_update(self, user_id, credential_data):
        """Emit credential update to user"""
        self.emit_to_user(user_id, 'credential_update', credential_data)

    def join_user_room(self, user_id, sid):
        """Join user to their personal room"""
        room_name = f"user_{user_id}"
        join_room(room_name)
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = []
        if room_name not in self.user_rooms[user_id]:
            self.user_rooms[user_id].append(room_name)

    def leave_user_room(self, user_id, sid):
        """Leave user from their personal room"""
        room_name = f"user_{user_id}"
        leave_room(room_name)
        if user_id in self.user_rooms and room_name in self.user_rooms[user_id]:
            self.user_rooms[user_id].remove(room_name)

# Global instance
websocket_service = WebSocketService()

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'status': 'success', 'timestamp': datetime.utcnow().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Remove user from connected users
    for user_id, sid in list(websocket_service.connected_users.items()):
        if sid == request.sid:
            websocket_service.leave_user_room(user_id, request.sid)
            del websocket_service.connected_users[user_id]
            break

@socketio.on('authenticate')
def handle_authenticate(data):
    """Handle user authentication for WebSocket"""
    try:
        token = data.get('token')
        if not token:
            emit('auth_error', {'error': 'No token provided'})
            return

        # Decode JWT token
        payload = decode_token(token)
        if not payload:
            emit('auth_error', {'error': 'Invalid token'})
            return

        user_id = payload.get('sub')
        if not user_id:
            emit('auth_error', {'error': 'Invalid user ID'})
            return

        # Store user connection
        websocket_service.connected_users[user_id] = request.sid
        websocket_service.join_user_room(user_id, request.sid)

        emit('authenticated', {
            'status': 'success',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })

        print(f"User {user_id} authenticated via WebSocket")

    except Exception as e:
        print(f"Authentication error: {e}")
        emit('auth_error', {'error': 'Authentication failed'})

@socketio.on('join_room')
def handle_join_room(data):
    """Handle joining a room"""
    try:
        room = data.get('room')
        if room:
            join_room(room)
            emit('room_joined', {'room': room, 'status': 'success'})
    except Exception as e:
        print(f"Join room error: {e}")
        emit('error', {'error': 'Failed to join room'})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle leaving a room"""
    try:
        room = data.get('room')
        if room:
            leave_room(room)
            emit('room_left', {'room': room, 'status': 'success'})
    except Exception as e:
        print(f"Leave room error: {e}")
        emit('error', {'error': 'Failed to leave room'})

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection health check"""
    emit('pong', {'timestamp': datetime.utcnow().isoformat()})