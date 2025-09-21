# Caminho: app/models/stakeholder.py

import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID

class Stakeholder(db.Model):
    __tablename__ = 'stakeholders'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)