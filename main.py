from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import List
from api_constants import mongdb_username, mongodb_pass, mongodb_hostname, mongdb_dbname
import urllib

DB_URI = "mongodb+srv://kishore:kishore123@cluster0.przuvs6.mongodb.net/?retryWrites=true&w=majority"


client = MongoClient(DB_URI)
db = client["bookstore"]
collection = db["books"]

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int

class BookWithID(Book):
    id: str

@app.get("/books", response_model=List[BookWithID])
async def get_books():
    books = list(collection.find())
    return [BookWithID(id=str(book["_id"]), **book) for book in books]

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if book:
        return Book(id=str(book["_id"]), **book)
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", response_model=List[Book])
async def add_books(books: List[Book]):
    try:
        inserted_books = []
        for book in books:
            result = collection.insert_one(book.dict())
            inserted_book = collection.find_one({"_id": result.inserted_id})
            inserted_books.append(inserted_book)
        return inserted_books
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to add books to the database")


from bson import ObjectId

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: str, book: Book):
    try:
        book_obj_id = ObjectId(book_id)
        result = collection.replace_one({"_id": book_obj_id}, book.dict())
        if result.matched_count:
            updated_book = collection.find_one({"_id": book_obj_id})
            return updated_book
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to update book in the database")

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    try:
        book_obj_id = ObjectId(book_id)
        result = collection.delete_one({"_id": book_obj_id})
        if result.deleted_count:
            return {"message": "Book deleted"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to delete book from the database")


@app.get("/search", response_model=List[Book])
async def search_books(title: str = Query(None, title="Title"), author: str = Query(None, title="Author"), min_price: float = Query(None, title="Minimum Price"), max_price: float = Query(None, title="Maximum Price")):
    try:
        query = {}
        if title:
            query["title"] = {"$regex": title, "$options": "i"}
        if author:
            query["author"] = {"$regex": author, "$options": "i"}
        if min_price is not None:
            query["price"] = {"$gte": min_price}
        if max_price is not None:
            query.setdefault("price", {})["$lte"] = max_price
        books = list(collection.find(query))
        return books
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to search books in the database")


@app.get("/search-with-index", response_model=List[Book])
async def search_books_with_index(title: str = Query(None, title="Title"), author: str = Query(None, title="Author")):
    try:
        query = {}
        if title:
            query["title"] = {"$regex": title, "$options": "i"}
        if author:
            query["author"] = {"$regex": author, "$options": "i"}

        index_hint = [("title", 1), ("author", 1)]

        books = list(collection.find(query).hint(index_hint))
        return books
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to search books in the database")



@app.get("/count")
async def get_books_count():
    pipeline = [
        {"$group": {"_id": None, "total_count": {"$sum": 1}}}
    ]
    try:
        cursor = collection.aggregate(pipeline)
        documents = []
        while True:
            try:
                document = cursor.next()
                documents.append(document)
            except StopAsyncIteration:
                break
            except StopIteration:
                break
        return documents
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve counts from the database")
