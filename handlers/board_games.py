from aiogram import Router

from handlers.actions import router as actions_router
from handlers.challenges import router as challenges_router
from handlers.moves import router as moves_router
from handlers.profiles import router as profiles_router
from handlers.top import router as top_router

router = Router()
router.include_router(challenges_router)
router.include_router(profiles_router)
router.include_router(top_router)
router.include_router(moves_router)
router.include_router(actions_router)
