import os
from deta import Deta
from fastapi import FastAPI, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
env = os.environ

deta = Deta(env.get("PROJECT_KEY"))
users = deta.Base("users")
images = deta.Drive("images")

@app.get("/")
def root():
    return {"message": env.get("HELLO", "EMPTY")}

@app.get("/users")
def get_users():
    # return users._fetch(buffer=1, last="7zbt2td6xf3h")
    return users.fetch(limit=10)

@app.post("/user")
def insert_new_user(user: dict):
    result = jsonable_encoder(users.insert(user))
    return JSONResponse(status_code=200, content=result)

@app.get("/user/{name}")
def get_user(name: str):
    result = jsonable_encoder(users.fetch({"name": name}))
    return JSONResponse(status_code=200, content=result)

@app.patch("/user/{key}")
def update_user(key: str, user: dict):
    result = jsonable_encoder(users.update(user, key))
    return JSONResponse(status_code=200, content=result)

@app.delete("/user/{key}")
def delete_user(key: str):
    users.delete(key)
    return JSONResponse(status_code=200, content={"message": "success"})

@app.get("/images")
def get_images():
    image_names = images.list().get('names', [])
    image_stream_generator = images.get(image_names[-1]).iter_chunks()
    image_bytes = b''.join(image_stream_generator)
    return Response(content=image_bytes, media_type="image/png")

@app.post("/image")
def insert_new_image(image: UploadFile):
    images.put(image.filename, image.file)
    return JSONResponse(status_code=200, content={"message": "success"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)