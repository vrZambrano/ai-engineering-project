from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import logging
import os
from api.endpoints import router

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="API Produção Vinhos EMBRAPA")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os headers
)

# Caminho para os arquivos do frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Monta os arquivos estáticos do frontend
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info(f"Frontend montado em: {frontend_path}")
else:
    logger.warning(f"Diretório do frontend não encontrado: {frontend_path}")

# Rota raiz que redireciona para o frontend
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

# Inclui o router com todos os endpoints da API
app.include_router(router)
