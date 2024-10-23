from app.db.crud.user import create_user, get_user_by_email, delete_user, get_user
from app.db.models.user import User, Role
from app.db.schemas.user import UserCreate
from sqlalchemy.orm import Session
import pytest

@pytest.fixture
def mock_db_session():
    """
    A pytest fixture that creates a temporary in-memory database session
    for testing purposes.  The session is created using the SQLite in-memory
    database engine, and the tables are created using the Base.metadata.create_all()
    method. The fixture yields the session object, and then closes it after the
    test is finished.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    # Create tables in the in-memory database
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)
    yield db
    db.close()

def test_create_user(mock_db_session: Session):
    user_data = UserCreate(email="test@test.com", password="test123", role=Role.PATIENT)
    new_user = create_user(mock_db_session, user_data)
    assert new_user.email == "test@test.com"
    assert new_user.password == "test123"
    assert new_user.role == Role.PATIENT

def test_get_user(mock_db_session: Session):
    user_data = UserCreate(email="test@test.com", password="test123", role=Role.PATIENT)
    new_user = create_user(mock_db_session, user_data)
    user = get_user(mock_db_session, user_id = new_user.user_id)
    assert user.email == "test@test.com"
    assert user.role == Role.PATIENT

def test_get_user_by_email(mock_db_session: Session):
    user_data = UserCreate(email="test@test.com", password="test123", role=Role.PATIENT)
    new_user = create_user(mock_db_session, user_data)
    user = get_user_by_email(mock_db_session, email="test@test.com")
    assert user.email == "test@test.com"
    assert user.role == Role.PATIENT

def test_delete_user(mock_db_session: Session):
    user_data = UserCreate(email="test@test.com", password="test123", role=Role.PATIENT)
    new_user = create_user(mock_db_session, user_data)
    deleted_user = delete_user(mock_db_session, user_id=new_user.user_id)
    assert deleted_user.email == "test@test.com"
    assert mock_db_session.query(User).filter(User.user_id == new_user.user_id).first() is None
