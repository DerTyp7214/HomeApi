#!/usr/bin/env python3

if __name__ == "__main__":
    import uvicorn
    from app import app, consts

    uvicorn.run(app, host="0.0.0.0", port=consts.port)
