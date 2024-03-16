from fastapi import FastAPI, APIRouter
from fastapi.security import HTTPBasic
from server.api.api import api_router
from server.api import deps
import socket
from decouple import config
import os


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP


HOST = config('HOST', default=extract_ip())
PORT = config('PORT', default=8091)

root_router = APIRouter()
security = HTTPBasic()
app = FastAPI(title="PrinterMDM")

app.include_router(api_router)

deps.Base.metadata.create_all(bind=deps.engine)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    #uvicorn.run(app, host=HOST, port=443, log_level="debug", ssl_keyfile="./localhost+3-key.pem" , ssl_certfile="./localhost+3.pem")
    uvicorn.run(app, host=HOST, port=PORT, log_level="debug")
    # start_web_ui = str('streamlit run ./web_ui/web_ui_console.py')
    # os.popen(start_web_ui)
