from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from werkzeug.exceptions import Conflict, NotFound
from application_business_rules.memo_handle_interactor import MemoHandleInteractor
from http import HTTPStatus

app = FastAPI()


@app.get('/memo/{memo_id}')
def get(memo_id):
    return JSONResponse(
        content={"message": MemoHandleInteractor().get(memo_id)}
    )


@app.post('/memo/{memo_id}')
async def post(memo_id, memo: str = Form(...)):
    return JSONResponse(
        content={"message": MemoHandleInteractor().save(memo_id, memo)}
    )


@app.put('/memo/{memo_id}')
async def put(memo_id, memo: str = Form(...)):
    return JSONResponse(
        content={"message": MemoHandleInteractor().update(memo_id, memo)}
    )


@app.exception_handler(NotFound)
async def handle_404(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"message": exc.description},
    )


@app.exception_handler(Conflict)
async def handle_409(request: Request, exc: Conflict):
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content={"message": exc.description},
    )
