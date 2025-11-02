from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core import validate_api_token, save_device, delete_device
from schemas import DeviceCreate, DeviceResponse
from typing import List

router = APIRouter(prefix="/api", tags=["devices"])

@router.post("/register_device", response_model=dict)
async def api_register_device(
    device_data: DeviceCreate,
    api_token: str,
    db: Session = Depends(get_db)
):
    user = validate_api_token(db, api_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    try:
        device = save_device(db, user.id, device_data)
        return {
            "status": "device_registered",
            "device_id": device.device_id,
            "device_token": device.device_token,
            "mode": "cloud"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Device registration failed: {str(e)}")

@router.post("/delete_device", response_model=dict)
async def api_delete_device(
    api_token: str,
    device_token: str,
    db: Session = Depends(get_db)
):
    success, message = delete_device(db, api_token, device_token)
    if success:
        return {
            "status": "device_deleted",
            "message": message
        }
    else:
        raise HTTPException(status_code=404, detail=message)

@router.get("/devices", response_model=dict)
async def api_devices(
    api_token: str,
    db: Session = Depends(get_db)
):
    user = validate_api_token(db, api_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    from models import Device
    from database import is_device_online
    
    devices = db.query(Device).filter(Device.user_id == user.id).all()
    devices_list = []
    
    for device in devices:
        online = is_device_online(device.last_seen)
        devices_list.append({
            "device_id": device.device_id,
            "device_token": device.device_token,
            "cloud": device.cloud,
            "online": online,
            "last_seen": device.last_seen,
            "poll_count": device.poll_count,
            "added": device.added
        })

    return {
        "user": user.username,
        "plan": user.plan,
        "devices_limit": user.devices_limit,
        "devices_count": len(devices_list),
        "devices": devices_list
    }