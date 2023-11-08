from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unique_id = Column(String, index=True, nullable=False)
    image_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    checksum = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String, nullable=False)
