#!/usr/bin/env python3

if __name__ == "__main__":
    import uvicorn
    from app import app, consts.port as port

    uvicorn.run(app, host="0.0.0.0", port=port)
