from fastapi import FastAPI, Request, status


app = FastAPI()


@app.get('/hello')
async def hello(request: Request):
    return {
        "status_code": status.HTTP_200_OK,
        "msg": f"Hey {request.client.host}:{request.client.port}"
    }
