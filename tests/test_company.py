from unittest.mock import patch

import pytest

from app.models.company import Company
from app.models.users import User


@pytest.mark.asyncio
async def test_create_with_owner(mock_db_session, company_data, user_data):
    owner = User(**user_data)
    company_data_with_owner = company_data.copy()
    company_data_with_owner["owner"] = owner

    with patch.object(
        Company, "create_with_owner", return_value=Company(**company_data_with_owner)
    ) as mock_create:
        company = await Company.create_with_owner(
            db=mock_db_session, **company_data_with_owner
        )

        assert company.name == company_data["name"]
        mock_create.assert_awaited_once_with(
            db=mock_db_session, **company_data_with_owner
        )


@pytest.mark.asyncio
async def test_get_by_id(mock_db_session, company_data):
    company_id = 1

    with patch.object(
        Company, "get_by_id", return_value=Company(**company_data)
    ) as mock_get_by_id:
        company = await Company.get_by_id(db=mock_db_session, company_id=company_id)

        assert company.name == company_data["name"]
        mock_get_by_id.assert_awaited_once_with(
            db=mock_db_session, company_id=company_id
        )


@pytest.mark.asyncio
async def test_get_my_company(mock_db_session, company_data):
    company_id = 1
    owner_id = 1

    with patch.object(
        Company, "get_my_company", return_value=Company(**company_data)
    ) as mock_get_my_company:
        company = await Company.get_my_company(
            db=mock_db_session, company_id=company_id, owner_id=owner_id
        )

        assert company.name == company_data["name"]
        mock_get_my_company.assert_awaited_once_with(
            db=mock_db_session, company_id=company_id, owner_id=owner_id
        )


@pytest.mark.asyncio
async def test_update_company(mock_db_session, company_data, faker):
    company_id = 1
    owner_id = 1
    updated_name = faker.company()
    updated_company_data = company_data.copy()
    updated_company_data["name"] = updated_name
    company = Company(**updated_company_data)

    with patch.object(Company, "update", return_value=company) as mock_update:
        updated_company = await Company.update(
            db=mock_db_session, company_id=company_id, user=owner_id, name=updated_name
        )

        assert updated_company.name == updated_name
        mock_update.assert_awaited_once_with(
            db=mock_db_session, company_id=company_id, user=owner_id, name=updated_name
        )


@pytest.mark.asyncio
async def test_delete_company(mock_db_session, company_data):
    company_id = 1
    owner_id = 1

    with patch.object(Company, "delete", return_value=None) as mock_delete:
        await Company.delete(
            db=mock_db_session, company_id=company_id, user_id=owner_id
        )

        mock_delete.assert_awaited_once_with(
            db=mock_db_session, company_id=company_id, user_id=owner_id
        )
