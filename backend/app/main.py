from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import routes

app = FastAPI(title='IPTV Service - Movistar Style')
app.include_router(routes.router, prefix='/api')

# serve prebuilt static frontend (placed in /app/static inside image)
app.mount('/', StaticFiles(directory='/app/static', html=True), name='static')
