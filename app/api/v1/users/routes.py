from fastapi import APIRouter

from .schema import UserLoginResponse
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
    response_model=UserLoginResponse,
    summary="User login",
    description="User login endpoint",
    status_code=200,
    response_description="User login successful",
    responses={
        200: {"description": "User login successful"},
        401: {"description": "Invalid login credentials"},
    },
)
