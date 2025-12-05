from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.algorithms import RSAAlgorithm
import httpx
from app.config import settings

JWKS_URL = f"https://cognito-idp.{settings.REGION}.amazonaws.com/{settings.USER_POOL_ID}/.well-known/jwks.json"

# Cache JWKS
jwks_cache = None

async def get_jwks():
    global jwks_cache
    if jwks_cache is None:
        async with httpx.AsyncClient() as client:
            r = await client.get(JWKS_URL)
            r.raise_for_status()
            jwks_cache = r.json()
    return jwks_cache

# Security
security = HTTPBearer()

async def verify_jwt(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token.credentials)
        kid = unverified_header['kid']
        key_data = next(k for k in jwks['keys'] if k['kid'] == kid)
        public_key = RSAAlgorithm.from_jwk(key_data)

        payload = jwt.decode(
            token.credentials,
            key=public_key,
            algorithms=[key_data['alg']],
            audience=settings.APP_CLIENT_ID
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def verify_admin(user = Depends(verify_jwt)):
    """Kiểm tra user có role admin không"""
    role = user.get("custom:role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập chức năng này"
        )
    return user

