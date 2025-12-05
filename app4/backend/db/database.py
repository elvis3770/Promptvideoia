"""
MongoDB Database Configuration and Connection
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
import os
from typing import Optional

class Database:
    """Singleton MongoDB database connection"""
    
    _instance: Optional['Database'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance
    
    async def connect(self):
        """Connect to MongoDB"""
        if self.client is None:
            mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client.video_commercial_generator
            
            # Create indexes
            await self.create_indexes()
            print("[OK] Connected to MongoDB")
    
    async def create_indexes(self):
        """Create indexes for optimized queries"""
        # Projects collection
        await self.db.projects.create_index("project_id", unique=True)
        await self.db.projects.create_index("status")
        await self.db.projects.create_index([("created_at", DESCENDING)])
        
        # Clips collection
        await self.db.clips.create_index("clip_id", unique=True)
        await self.db.clips.create_index("project_id")
        await self.db.clips.create_index([("project_id", ASCENDING), ("scene_id", ASCENDING)])
        await self.db.clips.create_index("status")
        
        # Assets collection
        await self.db.assets.create_index("asset_id", unique=True)
        await self.db.assets.create_index("project_id")
        await self.db.assets.create_index("type")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("[OK] MongoDB connection closed")

# Global database instance
db = Database()
