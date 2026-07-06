from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    yield
    # shutdown
    await engine.dispose()
