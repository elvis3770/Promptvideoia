"""
MongoDB Repositories for CRUD operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from ..db.database import db
from ..models.models import Project, Clip, Asset, ProjectStatus, ClipStatus

class ProjectRepository:
    """Repository for Project operations"""
    
    @staticmethod
    async def create(project: Project) -> str:
        """Create a new project"""
        project_dict = project.dict()
        project_dict['created_at'] = datetime.utcnow()
        project_dict['updated_at'] = datetime.utcnow()
        
        result = await db.db.projects.insert_one(project_dict)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_by_id(project_id: str) -> Optional[dict]:
        """Get project by project_id"""
        return await db.db.projects.find_one({"project_id": project_id})
    
    @staticmethod
    async def get_all(status: Optional[ProjectStatus] = None, limit: int = 50) -> List[dict]:
        """Get all projects with optional status filter"""
        query = {}
        if status:
            query['status'] = status.value
        
        cursor = db.db.projects.find(query).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    @staticmethod
    async def update(project_id: str, updates: dict) -> bool:
        """Update project"""
        updates['updated_at'] = datetime.utcnow()
        result = await db.db.projects.update_one(
            {"project_id": project_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def update_scene_status(project_id: str, scene_id: int, status: ClipStatus, clip_id: Optional[str] = None) -> bool:
        """Update status of a specific scene"""
        update_data = {
            "scenes.$.status": status.value,
            "updated_at": datetime.utcnow()
        }
        if clip_id:
            update_data["scenes.$.clip_id"] = clip_id
        
        result = await db.db.projects.update_one(
            {"project_id": project_id, "scenes.scene_id": scene_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def delete(project_id: str) -> bool:
        """Delete project"""
        result = await db.db.projects.delete_one({"project_id": project_id})
        return result.deleted_count > 0

class ClipRepository:
    """Repository for Clip operations"""
    
    @staticmethod
    async def create(clip: Clip) -> str:
        """Create a new clip"""
        clip_dict = clip.dict()
        clip_dict['created_at'] = datetime.utcnow()
        
        result = await db.db.clips.insert_one(clip_dict)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_by_id(clip_id: str) -> Optional[dict]:
        """Get clip by clip_id"""
        return await db.db.clips.find_one({"clip_id": clip_id})
    
    @staticmethod
    async def get_by_project(project_id: str) -> List[dict]:
        """Get all clips for a project"""
        cursor = db.db.clips.find({"project_id": project_id}).sort("scene_id", 1)
        return await cursor.to_list(length=100)
    
    @staticmethod
    async def get_by_scene(project_id: str, scene_id: int) -> Optional[dict]:
        """Get clip for specific scene"""
        return await db.db.clips.find_one({
            "project_id": project_id,
            "scene_id": scene_id
        })
    
    @staticmethod
    async def update(clip_id: str, updates: dict) -> bool:
        """Update clip"""
        result = await db.db.clips.update_one(
            {"clip_id": clip_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def update_status(clip_id: str, status: ClipStatus) -> bool:
        """Update clip status"""
        return await ClipRepository.update(clip_id, {"status": status.value})
    
    @staticmethod
    async def delete(clip_id: str) -> bool:
        """Delete clip"""
        result = await db.db.clips.delete_one({"clip_id": clip_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def delete_by_project(project_id: str) -> int:
        """Delete all clips for a project"""
        result = await db.db.clips.delete_many({"project_id": project_id})
        return result.deleted_count

class AssetRepository:
    """Repository for Asset operations"""
    
    @staticmethod
    async def create(asset: Asset) -> str:
        """Create a new asset"""
        asset_dict = asset.dict()
        asset_dict['uploaded_at'] = datetime.utcnow()
        
        result = await db.db.assets.insert_one(asset_dict)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_by_id(asset_id: str) -> Optional[dict]:
        """Get asset by asset_id"""
        return await db.db.assets.find_one({"asset_id": asset_id})
    
    @staticmethod
    async def get_by_project(project_id: str, asset_type: Optional[str] = None) -> List[dict]:
        """Get all assets for a project"""
        query = {"project_id": project_id}
        if asset_type:
            query['type'] = asset_type
        
        cursor = db.db.assets.find(query).sort("uploaded_at", -1)
        return await cursor.to_list(length=100)
    
    @staticmethod
    async def update(asset_id: str, updates: dict) -> bool:
        """Update asset"""
        result = await db.db.assets.update_one(
            {"asset_id": asset_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def delete(asset_id: str) -> bool:
        """Delete asset"""
        result = await db.db.assets.delete_one({"asset_id": asset_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def delete_by_project(project_id: str) -> int:
        """Delete all assets for a project"""
        result = await db.db.assets.delete_many({"project_id": project_id})
        return result.deleted_count
