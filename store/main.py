import json
from datetime import datetime
from typing import Set, Dict, List

from fastapi import Depends
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, field_validator
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

# FastAPI app setup
app = FastAPI()
# SQLAlchemy setup
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("user_id", Integer),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to read data from the database
def read_data(db: Session):
    # Query data using the session
    query_result = db.query(processed_agent_data).all()
    return query_result


# SQLAlchemy model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: float
    longitude: float


class AgentData(BaseModel):
    user_id: int
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


# Define a Pydantic model for response purposes
class ProcessedAgentDataResponse(BaseModel):
    id: int
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


# WebSocket subscriptions
subscriptions: Dict[int, Set[WebSocket]] = {}


# FastAPI WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)


# Function to send data to subscribed users
async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            await websocket.send_json(json.dumps(data))


# FastAPI CRUD endpoints

@app.post("/processed_agent_data/")
def create_processed_agent_data(data: ProcessedAgentData, db: Session = Depends(get_db)):
    db_processed_agent_data = ProcessedAgentDataInDB(**data.dict())
    db.add(db_processed_agent_data)
    db.commit()
    db.refresh(db_processed_agent_data)
    return db_processed_agent_data


# Read
@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataResponse)
def read_processed_agent_data(processed_agent_data_id: int, db: Session = Depends(get_db)):
    db_processed_agent_data = db.query(ProcessedAgentData).filter(
        ProcessedAgentData.id == processed_agent_data_id).first()
    if db_processed_agent_data is None:
        raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
    return db_processed_agent_data


# List
@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataResponse])
def list_processed_agent_data(db: Session = Depends(get_db)):
    # print("????????????????? GET REQUEST ???????????????????")
    # db = next(get_db())
    # try:
    #     # Read data from the database
    #     data = read_data(db)
    #     print(data)
    # finally:
    #     # Close the session
    #     db.close()

    db_processed_agent_data = db.query(ProcessedAgentData).all()
    return db_processed_agent_data


# Update
@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataResponse)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData, db: Session = Depends(get_db)):
    db_processed_agent_data = db.query(ProcessedAgentData).filter(
        ProcessedAgentData.id == processed_agent_data_id).first()
    if db_processed_agent_data is None:
        raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_processed_agent_data, key, value)
    db.commit()
    db.refresh(db_processed_agent_data)
    return db_processed_agent_data


# Delete
@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataResponse)
def delete_processed_agent_data(processed_agent_data_id: int, db: Session = Depends(get_db)):
    db_processed_agent_data = db.query(ProcessedAgentData).filter(
        ProcessedAgentData.id == processed_agent_data_id).first()
    if db_processed_agent_data is None:
        raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
    db.delete(db_processed_agent_data)
    db.commit()
    return db_processed_agent_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
