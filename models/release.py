import enum
import re
import uuid
from sqlalchemy import URL, UUID, Boolean, ForeignKey, Integer, String, UniqueConstraint
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped, validates
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from . import Base
from sqlalchemy.types import Enum
from sqlalchemy import INTEGER, TIMESTAMP, Column, String, text
from sqlalchemy import INTEGER, TIMESTAMP, Column, String, text


class ReleaseStates(enum.Enum):
    testing = 1
    ready_for_testing = 2
    tested = 3
    blocked = 4
    ready_for_release = 5
    released = 6
    stable = 7


class Environments(enum.Enum):
    dev = 1
    qa = 2
    beta = 3
    production = 4


class DeploymentStatus(enum.Enum):
    running = 1
    failed = 2
    success = 3


class Releases(Base):
    __tablename__ = 'releases'
    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    state = Column(Enum(ReleaseStates),
                   default=ReleaseStates.ready_for_testing)
    created_on = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))


class ReleaseActions(Base):
    __tablename__ = 'release_actions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_id = Column(Integer, ForeignKey('releases.id'), nullable=False)
    env = Column(Enum(Environments), nullable=False, default=Environments.dev)
    tag_url = Column(String(127), nullable=False)
    comment = Column(String(127), nullable=False)
    version = Column(String(15), nullable=False, )
    deployment_status = Column(Enum(DeploymentStatus), nullable=False)
    action_url = Column(String(127), nullable=False, unique=True)
    created_on = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    __table_args__ = (
        UniqueConstraint('version', 'env', name='uq_version_env'),
    )

    @validates('version')
    def validate_version(self, key, version):
        pattern = re.compile(r'^\d+\.\d+\.\d+$')
        if not pattern.match(version):
            raise ValueError(
                "Version must be in the format 'major.minor.patch'")
        return version


class ReleaseActionApprovals(Base):
    __tablename__ = 'release_action_approvals'
    id = Column(Integer, primary_key=True)
    release_action_id = Column(UUID(as_uuid=True), ForeignKey(
        'release_actions.id'), nullable=False)
    approved_by = Column(String, nullable=False)
    approved = Column(Boolean, nullable=False)


class ReleaseComments(Base):
    __tablename__ = 'release_comments'
    id = Column(Integer, primary_key=True)
    release_action_id = Column(UUID(as_uuid=True), ForeignKey(
        'release_actions.id'), nullable=False)
    comment = Column(String, nullable=False)
    commented_by = Column(String, nullable=False)
    created_on = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
