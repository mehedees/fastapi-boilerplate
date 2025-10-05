from fastapi import APIRouter

from app.core.schemas.base import APIResponse

from .schema import LoginToken, UserProfile
from .views import UserViews

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

user_router.add_api_route(
    "/login",
    endpoint=UserViews.login,
    methods=["POST"],
    name="login",
    response_model=LoginToken,
    summary="User login",
    description="User login endpoint",
    status_code=200,
    response_description="Login successful",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid login credentials"},
    },
)

user_router.add_api_route(
    "/me",
    endpoint=UserViews.me,
    methods=["GET"],
    name="me",
    response_model=APIResponse[UserProfile],
    summary="User profile",
    description="User profile endpoint",
    status_code=200,
    response_description="User profile retrieved",
    responses={
        200: {"description": "User profile retrieved"},
        404: {"description": "User not found"},
    },
)

user_router.add_api_route(
    "/refresh-token",
    endpoint=UserViews.refresh_token,
    methods=["POST"],
    name="refresh_token",
    response_model=LoginToken,
    summary="User token refresh",
    description="User token refresh endpoint",
    status_code=200,
    response_description="Refresh successful",
    responses={
        200: {"description": "Refresh successful"},
        401: {"description": "Invalid refresh token"},
    },
)
