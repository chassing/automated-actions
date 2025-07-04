from fastapi import APIRouter, Depends

from .dependencies import get_authz, get_user
from .views.action import router as action_router
from .views.admin import router as admin_router
from .views.external_resource import router as external_resource_router
from .views.no_op import router as no_op_router
from .views.openshift import router as openshift_router
from .views.user import router as user_router

router = APIRouter()
router.include_router(
    admin_router, dependencies=[Depends(get_user), Depends(get_authz)]
)
router.include_router(
    external_resource_router, dependencies=[Depends(get_user), Depends(get_authz)]
)
router.include_router(
    openshift_router, dependencies=[Depends(get_user), Depends(get_authz)]
)
router.include_router(
    action_router, dependencies=[Depends(get_user), Depends(get_authz)]
)
router.include_router(user_router, dependencies=[Depends(get_authz)])
router.include_router(no_op_router, dependencies=[Depends(get_authz)])
