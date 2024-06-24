import os
import uuid
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware

from main import ReleaseManager, get_db

# Configuration parameters
ORG = os.getenv("GITHUB_ORG", "loophealth")
REPO = os.getenv("GITHUB_REPO", "loop-backend")
WORKFLOW_FILE = os.getenv("GITHUB_WORKFLOW_FILE", "deploy_backend.yml")


# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize ReleaseManager
release_manager = ReleaseManager(ORG, REPO, WORKFLOW_FILE)

# Pydantic models


class ReleaseCreate(BaseModel):
    name: str


class HotfixCreate(BaseModel):
    release_id: int
    commits: List[str]


class CommentCreate(BaseModel):
    release_action_id: str
    comment: str
    commented_by: str


class ApprovalCreate(BaseModel):
    release_id: int
    approved_by: str


class Release(BaseModel):
    id: int
    name: str
    state: str

    class Config:
        orm_mode = True


class ReleaseAction(BaseModel):
    id: uuid.UUID
    release_id: int
    env: str
    tag_url: str
    comment: str
    version: str
    deployment_status: str
    action_url: str

    class Config:
        orm_mode = True


class ReleaseComment(BaseModel):
    id: int
    release_action_id: uuid.UUID
    comment: str
    commented_by: str

    class Config:
        orm_mode = True


class ReleaseApproval(BaseModel):
    id: int
    release_action_id: uuid.UUID
    approved_by: str

    class Config:
        orm_mode = True

# API Endpoints


# API Endpoints

# Releases
@app.post("/releases/", response_model=Release, tags=["Releases"])
def create_release(release: ReleaseCreate):
    release = release_manager.create_release("main", release.name)
    return release


@app.get("/releases/{release_id}", response_model=Release, tags=["Releases"])
def read_release(release_id: int):
    try:
        release = release_manager.get_release(release_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return release


@app.get("/releases/", response_model=List[Release], tags=["Releases"])
def list_releases():
    return release_manager.list_releases()


@app.post("/releases/{release_id}/promote", tags=["Releases"])
def promote_release(release_id: int):
    try:
        release_manager.promote_release(release_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Release promoted"}


@app.post("/releases/{release_id}/block", tags=["Releases"])
def block_release(release_id: int):
    try:
        release_manager.block_release(release_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Release blocked"}

# Release Actions


@app.get("/releases/{release_id}/actions", response_model=List[ReleaseAction], tags=["Release Actions"])
def list_release_actions(release_id: int):
    return release_manager.get_release_actions(release_id)

# Comments


@app.post("/comments/", response_model=CommentCreate, tags=["Comments"])
def comment_on_release(comment: CommentCreate):
    try:
        release_manager.comment_on_release(
            comment.release_action_id, comment.comment, comment.commented_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return comment


@app.get("/release-actions/{release_action_id}/comments", response_model=List[ReleaseComment], tags=["Comments"])
def list_release_comments(release_action_id: uuid.UUID):
    return release_manager.get_release_comments(release_action_id)

# Approvals


@app.post("/approvals/", response_model=ApprovalCreate, tags=["Approvals"])
def approve_release(approval: ApprovalCreate):
    try:
        release_manager.approve_release(
            approval.release_id, approval.approved_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return approval


@app.get("/releases/{release_id}/approvals", response_model=List[ReleaseApproval], tags=["Approvals"])
def list_approvals(release_id: int):
    return release_manager.get_approvals(release_id)


@app.post("/releases/{release_id}/hotfix", tags=["Releases"])
def hotfix_release(hotfix: HotfixCreate):
    try:
        release_manager.hotfix(hotfix.release_id, hotfix.commits)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Hotfix applied"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
