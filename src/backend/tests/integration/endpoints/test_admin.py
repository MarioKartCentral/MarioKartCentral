import pytest
from starlette.testclient import TestClient
from tests.integration.types import UserClientFactory


class TestBackupDBRoute:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("role_name", [
        "Super Moderator",
        "Site Moderator",
        "Support Staff",
        "Lounge Staff",
        "Event Admin",
        "Event Mod",
        "Banned",
        "Team Leader Banned",
        "Time Trial Admin",
        None,
    ])
    async def test_backup_db_route_raises_403(user_client_factory: UserClientFactory, role_name: str | None):
        client = await user_client_factory(role_name)
        response = client.post(
            "/api/admin/db_backup"
        )
        assert response.status_code == 403

    @staticmethod
    def test_backup_db_route_anon_raises_401(client: TestClient):
        response = client.post(
            "api/admin/db_backup"
        )

        assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("role_name", [
        "Super Administrator",
        "Administrator",
    ])
    async def test_backup_db_route_admin(user_client_factory: UserClientFactory, role_name: str):
        client = await user_client_factory(role_name)
        response = client.post(
            "/api/admin/db_backup"
        )
        assert response.status_code == 204
