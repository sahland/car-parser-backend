from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.get("/img-proxy/")
async def img_proxy(url: str):
    try:
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = await client.get(url, headers=headers)
        return Response(content=resp.content, media_type=resp.headers.get("content-type"))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=500)
