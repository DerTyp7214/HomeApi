if __name__ == "__main__":
    import uvicorn
    from decouple import config
    from app import app

    uvicorn.run(app, host="0.0.0.0", port=int(config("port", default="8000")))
