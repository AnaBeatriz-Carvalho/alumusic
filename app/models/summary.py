# Caminho: app/models/summary.py

import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class WeeklySummary(db.Model):
    __tablename__ = 'weekly_summaries'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WeeklySummary {self.start_date} to {self.end_date}>'