import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# FastAPI アプリケーションの初期化
app = FastAPI()

# ロガーの設定
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO

# イメージファイルが保存されているディレクトリのパス
images = pathlib.Path(__file__).parent.resolve() / "images"

# CORS 設定
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# JSONファイルのパスを指定
json_file_path = pathlib.Path(__file__).parent.resolve() / "items.json"

@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(None), image: UploadFile = File(...)):
    # 受け取ったアイテムの情報をログに記録
    # logger.info(f"Receive item: {name}, Category: {category}")

    # 画像ファイルの内容を読み込み、SHA256 ハッシュでファイル名を生成
    image_data = await image.read()
    image_hash = hashlib.sha256(image_data).hexdigest()
    image_filename = f"{image_hash}.jpg"

    # 画像を保存
    with open(images / image_filename, "wb") as image_file:
        image_file.write(image_data)

    # 新しいアイテムを辞書形式で作成
    new_item = {"name": name, "category": category, "image": image_filename}

    item_message = f"Item received: {name} "
    if category:
        item_message += f" Category: '{category}'."

    # JSONファイルを読み込み、アイテムを追加
    if json_file_path.exists():
        with open(json_file_path, "r+", encoding="utf-8") as file:
            try:
                data = json.load(file)  # JSONデータの読み込み
            except json.JSONDecodeError:
                data = {"items": []}  # JSONファイルが空または不正な場合、デフォルトのデータ構造を使用
            data["items"].append(new_item)
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
    else:
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump({"items": [new_item]}, file, indent=4)
    
    # アイテムが正常に追加されたことをクライアントに通知
    return {"message": f"Item '{name}' with image '{image_filename}' received and saved."}

@app.get("/items")
def get_items():
    # JSONファイルが存在しない場合は空のリストを返す
    if not json_file_path.exists():
        return {"items": []}
    
    # JSONファイルからアイテムのリストを読み込む
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data
    
@app.get("/image/{image_name}")
async def get_image(image_name):
    # image pathの作成
    image = images / image_name

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image not found")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.get("/items/{item_id}")
def get_item(item_id: int):
    # JSONファイルが存在しない場合はエラーを返す
    if not json_file_path.exists():
        raise HTTPException(status_code=404, detail="Items not found")

    # JSONファイルからアイテムのリストを読み込む
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        items = data.get("items", [])

    # item_id がリストの範囲外の場合はエラーを返す
    if item_id < 1 or item_id > len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    # 指定された item_id のアイテムを返す（リストは 0 から始まるので、item_id から 1 を引く）
    return items[item_id - 1]
