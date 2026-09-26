from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.auth_routes import router as auth_router
from backend.routes.emergency_routes import router as emergency_router
from backend.routes.resource_routes import router as resource_router
from backend.services.priority_service import model_status

app = FastAPI(title='ResQNet Emergency Response API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8501'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(auth_router)
app.include_router(emergency_router)
app.include_router(resource_router)


@app.get('/health')
def health():
    return {'status': 'ok', 'priority_model': model_status()}
