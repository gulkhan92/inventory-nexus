import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.models.domain import User


def create_guest_token(user: User) -> str:
    settings = get_settings()
    if not settings.superset_dashboard_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Superset dashboard id is not configured",
        )

    base_url = settings.superset_base_url.rstrip("/")
    with httpx.Client(base_url=base_url, timeout=15.0) as client:
        login_response = client.post(
            "/api/v1/security/login",
            json={
                "username": settings.superset_username,
                "password": settings.superset_password,
                "provider": "db",
                "refresh": True,
            },
        )
        if login_response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to authenticate with Superset",
            )

        access_token = login_response.json().get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Superset login did not return an access token",
            )

        guest_response = client.post(
            "/api/v1/security/guest_token",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "resources": [
                    {"type": "dashboard", "id": settings.superset_dashboard_id}
                ],
                "rls": [],
                "user": {
                    # Superset uses 'username' as the identity key in some setups.
                    "username": user.email,
                    "first_name": user.full_name,
                    "last_name": "",
                },
            },
        )
        if guest_response.status_code >= 400:
            # Include response text to make debugging configuration/token issues easier.
            detail = (
                "Unable to create Superset guest token: "
                f"status={guest_response.status_code}, body={guest_response.text[:1000]}"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=detail,
            )

        try:
            payload = guest_response.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Superset guest token response was not valid JSON: {guest_response.text[:1000]}",
            )

        token = payload.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Superset guest token response did not include a token. Body={guest_response.text[:1000]}",
            )
        return token
