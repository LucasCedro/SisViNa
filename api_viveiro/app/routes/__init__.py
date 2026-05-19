from app.routes.especies import router as especies_router
from app.routes.plantas import router as plantas_router
# ... outros routers

routers = [
    especies_router,
    plantas_router,
    # ... adicione todos os routers aqui
]