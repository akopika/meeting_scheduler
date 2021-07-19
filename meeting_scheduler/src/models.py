from datetimerange import DateTimeRange
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    timeslots = db.relationship(
        'Timeslot',
        backref='user',
        lazy=True,
        cascade="all, delete"
    )
    meetings = db.relationship(
        'Meeting',
        backref='host',
        lazy=True,
        cascade="all, delete"
    )

    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def __repr__(self):
        return f'<User: {self.username}>'

    def check_password(self, password: str):
        return bcrypt.check_password_hash(self.password, password)


class Timeslot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Timeslot: {self.start_time}-{self.end_time} for {self.user}>'


participants = db.Table(
    'participant',
    db.Column(
        'participant_id',
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True
    ),
    db.Column(
        'meeting_id',
        db.Integer,
        db.ForeignKey('meeting.id'),
        primary_key=True
    )
)


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meeting_start_time = db.Column(db.DateTime, nullable=False)
    meeting_end_time = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(32), nullable=False)
    comment = db.Column(db.String(256))
    link = db.Column(db.String(64), nullable=False)
    details = db.Column(db.String(64), nullable=False)
    participants = db.relationship(
        'User',
        secondary=participants,
        lazy='subquery',
        backref=db.backref('invitations', lazy=True)
    )

    def check_overlaps(self, meeting_to_update=None):
        host = self.host
        host_meetings = \
            [m for m in host.meetings + host.invitations
             if m != meeting_to_update]
        for h_meeting in host_meetings:
            if DateTimeRange(h_meeting.meeting_start_time,
                             h_meeting.meeting_end_time).is_intersection(
                    DateTimeRange(self.meeting_start_time,
                                  self.meeting_end_time)):
                return False
        participants = self.participants
        for participant in participants:
            participant_meetings = \
                [meeting for meeting in participant.meetings + participant.invitations
                 if meeting != meeting]
            for p_meeting in participant_meetings:
                if DateTimeRange(p_meeting.meeting_start_time,
                                 p_meeting.meeting_end_time).is_intersection(
                        DateTimeRange(self.meeting_start_time,
                                      self.meeting_end_time)):
                    return False
        return True

    def __repr__(self):
        return f'<Meeting: {self.meeting_start_time}' \
               f'-{self.meeting_start_time} for {self.host}>'
