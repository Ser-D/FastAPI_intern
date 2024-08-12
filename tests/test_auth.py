from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.exc import IntegrityError

from app.models.users import User
from app.schemas.users import SignInRequest, SignUpRequest
from app.services.auth import auth_service


@pytest.fixture
def user_data():
    return {
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "hashed_password": "hashed_password",
        "is_active": True,
    }


@pytest.fixture
def signup_request():
    return SignUpRequest(
        firstname="Test",
        lastname="User",
        email="testuser@example.com",
        password1="password",
        password2="password",
    )


@pytest.mark.asyncio
async def test_create_user_success(mock_db_session, signup_request, user_data):
    new_user = User(**user_data)
    with patch.object(User, "create", new_callable=AsyncMock, return_value=new_user):
        user = await auth_service.create_user(mock_db_session, **signup_request.model_dump())
        assert user.email == new_user.email


@pytest.mark.asyncio
async def test_create_user_duplicate(mock_db_session, signup_request, user_data):
    error = IntegrityError(
        "(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint",
        params={},
        orig=Exception("duplicate"),
    )

    with patch.object(User, "create", new_callable=AsyncMock, side_effect=error):
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.create_user(mock_db_session, **signup_request.model_dump())

        assert excinfo.value.status_code == 409
        assert excinfo.value.detail == "Account already exists"


@pytest.fixture
def signin_request():
    return SignInRequest(email="testuser@example.com", password="password")


@pytest.mark.asyncio
async def test_authenticate_user_success(mock_db_session, user_data, signin_request):
    user = User(**user_data)
    with patch.object(User, "get_user_by_email", new_callable=AsyncMock, return_value=user):
        with patch.object(auth_service, "verify_password", return_value=True):
            authenticated_user = await auth_service.authenticate_user(
                mock_db_session, signin_request.email, signin_request.password
            )
            assert authenticated_user.email == user.email


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(mock_db_session, signin_request):
    with patch.object(User, "get_user_by_email", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.authenticate_user(mock_db_session, signin_request.email, signin_request.password)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Invalid credentials"


@pytest.fixture
def user_data():
    return {
        "id": 1,
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "hashed_password": "hashed_password",
        "is_active": True,
    }


@pytest.mark.asyncio
async def test_get_current_user_success(mock_db_session, user_data):
    user = User(**user_data)

    token_data = {"sub": user.email, "scope": "access_token"}
    secret_key = auth_service.SECRET_KEY
    algorithm = auth_service.ALGORITHM
    token = jwt.encode(token_data, secret_key, algorithm=algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch.object(
        auth_service,
        "check_token_auth0",
        new_callable=AsyncMock,
        return_value=user.email,
    ):
        with patch.object(auth_service.cache, "get", return_value=None):
            with patch.object(auth_service.cache, "set", return_value=None):
                with patch.object(auth_service.cache, "expire", return_value=None):
                    with patch.object(
                        User,
                        "get_user_by_email",
                        new_callable=AsyncMock,
                        return_value=user,
                    ):
                        current_user = await auth_service.get_current_user(credentials, mock_db_session)
                        assert current_user.email == user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db_session, user_data):
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

    with patch.object(
        auth_service,
        "check_token_auth0",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=401, detail="Could not validate credentials"),
    ):
        with pytest.raises(HTTPException) as excinfo:
            await auth_service.get_current_user(token, mock_db_session)

        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_create_access_token_success():
    data = {"sub": "test@example.com"}
    token = await auth_service.create_access_token(data)
    assert token is not None
    payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
    assert payload["sub"] == data["sub"]


@pytest.mark.asyncio
async def test_decode_refresh_token_success():
    data = {"sub": "test@example.com"}
    refresh_token = await auth_service.create_refresh_token(data)
    email = await auth_service.decode_refresh_token(refresh_token)
    assert email == data["sub"]


@pytest.mark.asyncio
async def test_decode_refresh_token_invalid_scope():
    invalid_token = jwt.encode(
        {"sub": "test@example.com", "scope": "access_token"},
        auth_service.SECRET_KEY,
        algorithm=auth_service.ALGORITHM,
    )
    with pytest.raises(HTTPException) as excinfo:
        await auth_service.decode_refresh_token(invalid_token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid scope for token"


@pytest.mark.asyncio
async def test_check_token_auth0_success(mock_db_session, user_data):
    token = "valid_jwt_token"
    email = user_data["email"]
    user = User(**user_data)

    with patch.object(auth_service, "load_public_key_from_cert", return_value="public_key"):
        with patch.object(jwt, "decode", return_value={"email": email}):
            with patch.object(User, "get_user_by_email", new_callable=AsyncMock, return_value=user):
                result = await auth_service.check_token_auth0(token, mock_db_session)
                assert result == email


@pytest.mark.asyncio
async def test_check_token_auth0_no_email(mock_db_session):
    token = "valid_jwt_token"

    with patch.object(auth_service, "load_public_key_from_cert", return_value="public_key"):
        with patch.object(jwt, "decode", return_value={}):
            with pytest.raises(HTTPException) as excinfo:
                await auth_service.check_token_auth0(token, mock_db_session)
            assert excinfo.value.status_code == 401
            assert excinfo.value.detail == "Email not found in token"


@pytest.mark.asyncio
async def test_check_token_auth0_invalid_token(mock_db_session):
    token = "invalid_jwt_token"

    with patch.object(auth_service, "load_public_key_from_cert", return_value="public_key"):
        with patch.object(jwt, "decode", side_effect=jwt.JWTError):
            with pytest.raises(HTTPException) as excinfo:
                await auth_service.check_token_auth0(token, mock_db_session)
            assert excinfo.value.status_code == 401
            assert excinfo.value.detail == "Invalid token"
