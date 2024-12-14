# app/api/v1/endpoints/websocket.py

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime

from app.api.deps import get_db, get_websocket_user
from app.models.user import User
from app.models.prompt import PromptType
from app.schemas.news import NewsArticleResponse

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "public": [],
            "internal": [],
            "private": {}  # Dict of user_id: [connections]
        }

    async def connect(
        self,
        websocket: WebSocket,
        user: Optional[User] = None
    ):
        await websocket.accept()
        
        # Add to public connections
        self.active_connections["public"].append(websocket)
        
        if user:
            # Add to internal connections if authenticated
            self.active_connections["internal"].append(websocket)
            
            # Initialize user's private connections if needed
            user_id = str(user.id)
            if user_id not in self.active_connections["private"]:
                self.active_connections["private"][user_id] = []
            self.active_connections["private"][user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user: Optional[User] = None):
        # Remove from public connections
        if websocket in self.active_connections["public"]:
            self.active_connections["public"].remove(websocket)
        
        if user:
            # Remove from internal connections
            if websocket in self.active_connections["internal"]:
                self.active_connections["internal"].remove(websocket)
            
            # Remove from private connections
            user_id = str(user.id)
            if user_id in self.active_connections["private"]:
                if websocket in self.active_connections["private"][user_id]:
                    self.active_connections["private"][user_id].remove(websocket)
                if not self.active_connections["private"][user_id]:
                    del self.active_connections["private"][user_id]

    async def broadcast_news(
        self,
        news: NewsArticleResponse,
        prompt_type: PromptType,
        user_id: Optional[UUID] = None
    ):
        """Broadcast news to appropriate connections based on type."""
        message = {
            "type": "news_update",
            "data": news.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Convert to JSON string
        json_message = json.dumps(message)
        
        # Broadcast based on prompt type
        if prompt_type == PromptType.PUBLIC:
            await self._broadcast_to_connections(self.active_connections["public"], json_message)
        
        elif prompt_type == PromptType.INTERNAL:
            await self._broadcast_to_connections(self.active_connections["internal"], json_message)
        
        elif prompt_type == PromptType.PRIVATE and user_id:
            user_connections = self.active_connections["private"].get(str(user_id), [])
            await self._broadcast_to_connections(user_connections, json_message)

    async def _broadcast_to_connections(
        self,
        connections: List[WebSocket],
        message: str
    ):
        """Helper method to broadcast message to list of connections."""
        for connection in connections.copy():  # Use copy to avoid modification during iteration
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                # Connection is dead, remove it
                if isinstance(connections, list):
                    connections.remove(connection)
            except Exception as e:
                print(f"Error broadcasting message: {str(e)}")

manager = ConnectionManager()

@router.websocket("/news-updates")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time news updates."""
    user = await get_websocket_user(websocket, db) if token else None
    
    try:
        await manager.connect(websocket, user)
        
        while True:
            try:
                # Keep the connection alive and handle any incoming messages
                data = await websocket.receive_text()
                # You could handle client messages here if needed
                
            except WebSocketDisconnect:
                manager.disconnect(websocket, user)
                break
                
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, user)

async def broadcast_new_article(
    article: NewsArticleResponse,
    prompt_type: PromptType,
    user_id: Optional[UUID] = None
):
    """Helper function to broadcast new articles."""
    await manager.broadcast_news(article, prompt_type, user_id)