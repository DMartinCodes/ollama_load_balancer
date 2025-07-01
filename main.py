from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.responses import StreamingResponse
from starlette.status import HTTP_502_BAD_GATEWAY
from router import forward_generic_request



app = FastAPI()

@app.api_route("/api/{path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])

async def proxy_api(request: Request, path: str):

    try:
        result = await forward_generic_request(request, path)
        return result
        
    except Exception as e:
        return JSONResponse(
            status_code=HTTP_502_BAD_GATEWAY,
            content={"error": f"Failed to proxy request: {str(e)}"},
        )
