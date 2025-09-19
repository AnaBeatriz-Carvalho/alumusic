import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID


class WeeklySummary(db.Model):
    __tablename__ = 'weekly_summaries'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    charts_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
