import os
import logging
import pathlib
import json
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, File, UploadFile, Query
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


DATABASE_URL = "db/new_mercari.sqlite3"

# データベース接続関数の作成
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得できるようにする
    return conn


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
    
    # データベース接続
    conn = get_db_connection()
    # cursor = conn.cursor()

    # 商品情報をデータベースに保存
    conn.execute("INSERT INTO items (name, category, image_name) VALUES (?, ?, ?)",
                 (name, category, image_filename))
    
    conn.commit()

    # データベース接続を閉じる
    conn.close()

    # アイテムが正常に追加されたことをクライアントに通知
    return {"id": conn.lastrowid, "name": name, "category": category, "image_name": image_filename}

@app.get("/items")
def get_items():
    conn = get_db_connection()
    items = conn.execute("""
        SELECT items.id, items.name, categories.name AS category, items.image_name
        FROM items
        JOIN categories ON items.category_id = categories.id
    """).fetchall()
    conn.close()

    # 結果をリストに変換
    items_list = [{"id": item["id"], "name": item["name"], "category": item["category"], "image_name": item["image_name"]} for item in items]

    return {"items": items_list}

    # JSONファイルが存在しない場合は空のリストを返す
    #if not json_file_path.exists():
        #return {"items": []}
    
    # JSONファイルからアイテムのリストを読み込む
    #with open(json_file_path, "r", encoding="utf-8") as file:
        #data = json.load(file)
        #return data


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

@app.get("/search")
def search_items(keyword: str = Query(None, min_length=1)):
    conn = get_db_connection()
    # LIKE句を使用して、キーワードを含む商品名を持つレコードを検索
    items = conn.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{keyword}%",)).fetchall()
    conn.close()

    items_list = [{"id": item["id"], "name": item["name"], "category": item["category"], "image_name": item["image_name"]} for item in items]

    return {"items": items_list}
