from __future__ import annotations
from typing import Optional, Any
import json
# pylint:disable=import-error
from overrides import overrides
# pylint:disable=import-error
import sqlalchemy as sa
from sqlalchemy import func
# mypy: disable_error_code="attr-defined, misc"
# Mypy saying DeclarativeBase isn't in sqlalchemy.orm. This should be an issue of an old version
# sqlalchemy stubs deprecated, missing types for DeclarativeBase
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from you_shall_not_parse.observer import Observer
from you_shall_not_parse.base_classes import Severity, IssueTupleType


class Base(DeclarativeBase):
    # pylint:disable=too-few-public-methods
    def as_dict(self) -> dict[str, str]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Issue(Base):
    # pylint:disable=too-few-public-methods
    __tablename__ = 'issues'
    id = sa.Column(sa.Integer, primary_key=True)
    linter_name = sa.Column(sa.String)
    file_path = sa.Column(sa.String)
    severity: sa.Column['Severity'] = sa.Column(sa.Enum(Severity))
    name = sa.Column(sa.String)
    message = sa.Column(sa.String)
    location = sa.Column(sa.String)


class Database:
    def __init__(self, filename: Optional[str] = None) -> None:
        if filename:
            self.engine = sa.create_engine(f'sqlite:///{filename}')
        else:
            self.engine = sa.create_engine('sqlite:///:memory:')

        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def add_issue(self, linter_name: str, issue: IssueTupleType) -> None:
        session = self.session()
        session.add(Issue(linter_name=linter_name,
                          severity=issue[0].name,
                          file_path=issue[1],
                          name=issue[2],
                          message=issue[3],
                          location=issue[4]))
        session.commit()

    def query(self, query_str: str, parameters: Optional[dict[str, str]] = None) -> Any:
        session = self.session()
        return session.execute(sa.sql.text(query_str), parameters).fetchall()

    def count(self, condition: str) -> Any:
        session = self.session()
        # pylint:disable=not-callable
        return session.query(func.count(Issue.id)).filter(sa.sql.text(condition)).scalar()

    def as_json(self) -> str:
        session = self.session()
        issues = session.query(Issue).all()
        return json.dumps([i.as_dict() for i in issues], default=str)



class DBObserver(Observer):
    def __init__(self, old_db: Optional[Database] = None, filename: Optional[str] = None) -> None:
        if old_db:
            self.database = old_db
        else:
            self.database = Database(filename)

    def get_database(self) -> Database:
        return self.database

    @overrides(check_signature=False)
    def add_issue(self, linter_name: str, issue: IssueTupleType) -> None:
        self.database.add_issue(linter_name, issue)
