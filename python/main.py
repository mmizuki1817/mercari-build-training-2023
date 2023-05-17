import hashlib
import json
import os
import os.path
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import sqlite3

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    logger.info(f"Receive item: {name}")
    
    # rename image to hash
    img = image
    if os.path.isfile(img) == True:
        copy = 'copy.jpg'
        shutil.copyfile(img, copy)
        with open(copy, 'rb') as copy_f:    
            sha256 = hashlib.sha256(copy_f.read()).hexdigest()
            ext = ".jpg"
            hash_img = sha256 + ext
            os.rename(copy, f"./images/{hash_img}")
    # Error handling (no image)
    else:
        logger.info("Image not found")
        hash_img = "..."

    #save info into a db file
    path = '../db/items.db'
    if os.path.isfile(path) == False:
        connect = sqlite3.connect(path)
        cursor = connect.cursor()
        cursor.execute("CREATE TABLE category(id integer PRIMARY KEY, name string unique)")
        cursor.execute("CREATE TABLE items(id integer PRIMARY KEY, name string, category_id integer, image_name string, FOREIGN KEY(category_id) REFERENCES category(id))")
    connect = sqlite3.connect(path)
    cursor = connect.cursor()
    cursor.execute("PRAGMA foreign_keys=True")
    cursor.execute("INSERT INTO category(name) values(?) ON CONFLICT(name) DO NOTHING", (category,))
    cursor.execute("SELECT id FROM category WHERE name=?", (category,))
    log = cursor.fetchone()
    i = int(log[0])
    cursor.execute("INSERT INTO items(name, category_id, image_name) values(?, ?, ?)", (name, i, hash_img))
    connect.commit()
    cursor.close()
    connect.close()
    return ({"message": f"item received: {name}"})

    '''
    #save info into a json file
    # add log to a json file
    log = { "items" : [
            {"name" : f"{name}",
             "category": f"{category}",
             "image_name" : f"{hash_img}"
            }]}
    
    try:
        with open('items.json', 'r') as f:
            # Error handling (empty json file)
            if os.path.getsize('items.json')== 0:
                with open('items.json', 'w') as f:
                        json.dump(log, f)
            else:
                read_data = json.load(f)
                save_data = [read_data, log]
                with open('items.json', 'w') as f:
                    json.dump(save_data, f)
    # Error handling(no file) 
    except FileNotFoundError:
        with open('items.json', 'w+') as f:
            json.dump(log, f)
    return ({"message": f"item received: {name}"})
    '''


@app.get("/items")
def show_list_of_items():
    # db info
    path = '../db/items.db'
    if os.path.isfile(path) == False:
        return ("no items")
    db = '../db/items.db'
    connect = sqlite3.connect(db)
    cursor = connect.cursor()
    cursor.execute("SELECT category.id, items.name, category.name, image_name FROM items INNER JOIN category ON items.category_id = category.id")
    log = cursor.fetchall()
    cursor.close()
    connect.close()
    return (log)

    '''
    # json info
    try:
        with open('items.json', 'r') as f:
            line = f.read()
            return (line)
        # 標準出力されるとき邪魔なエスケープ文字が入ってしまう
        # （print/logger.infoで出力するときはエスケープ文字は現れない）
    except FileNotFoundError:
        return ("no items")
    '''

@app.get("/search")
def search_items(keyword: str):
    path = '../db/items.db'
    if os.path.isfile(path) == False:
        return ("no items")
    db = '../db/items.db'
    connect = sqlite3.connect(db)
    cursor = connect.cursor()
    cursor.execute("SELECT json_object('items', (SELECT json_group_array(json_object('name', items.name, 'category', category.name, 'image_name', image_name))\
                   FROM items INNER JOIN category ON items.category_id = category.id \
                      WHERE items.name=? OR category.name=? OR image_name=?)) ", (keyword, keyword, keyword))
    data = cursor.fetchall()
    cursor.close()
    connect.close()
    # 出力にエスケープ文字が入ってしまう
    return (data)

# for json
'''
@app.get("/items/{item_id}")
def show_detail_of_item(item_id):
    try: 
        with open('items.json', 'r') as f:
            jsn = []
            jsn = json.load(f)
            # Error handling (invalid item_id)
            if item_id.isnumeric()==False or int(item_id) < 1 or int(item_id) > len(jsn):
                return("invalid id")
            return(jsn[int(item_id) - 1])
    except FileNotFoundError:
        return ("no items")
'''

#Optional課題、未着手
@app.get("/image/{image_name}")
async def get_image(image_name):
    # Create image path
    image = images / image_name

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)