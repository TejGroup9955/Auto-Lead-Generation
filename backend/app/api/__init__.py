from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .products import router as products_router
from .regions import router as regions_router
from .campaigns import router as campaigns_router
from .leads import router as leads_router
from .tags import router as tags_router
from .notes import router as notes_router
from .activity import router as activity_router
from .reports import router as reports_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(regions_router, prefix="/regions", tags=["Regions"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(leads_router, prefix="/leads", tags=["Leads"])
api_router.include_router(tags_router, prefix="/lead-tags", tags=["Lead Tags"])
api_router.include_router(notes_router, prefix="/lead-notes", tags=["Lead Notes"])
api_router.include_router(activity_router, prefix="/activity-logs", tags=["Activity Logs"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])