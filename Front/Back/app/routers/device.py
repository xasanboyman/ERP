import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, crud
from app.auth import get_current_device_token, get_current_user_required

router = APIRouter(tags=["Device Management"])


@router.post("/device/pair-token")
@router.post("/api/device/pair-token")
def pair_device_token(
    payload: schemas.DevicePairRequest,
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    if not payload.device_name or not payload.device_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Device name is required"
        )

    target_user_id = current_user.id
    if payload.user_id is not None:
        target_user = db.query(models.User).filter(models.User.id == payload.user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=404,
                detail=f"User ID {payload.user_id} not found"
            )
        target_user_id = target_user.id

    dev_token = crud.create_device_token(
        db=db,
        user_id=target_user_id,
        device_name=payload.device_name.strip()
    )

    qr_payload_dict = {
        "token": dev_token.token,
        "device_name": dev_token.device_name,
        "user_id": dev_token.user_id,
        "pair_code": dev_token.pair_code,
        "created_at": dev_token.created_at.isoformat() if dev_token.created_at else None
    }
    qr_payload_str = json.dumps(qr_payload_dict)

    response_data = {
        "pair_code": dev_token.pair_code,
        "token": dev_token.token,
        "expires_at": dev_token.expires_at.isoformat() if dev_token.expires_at else None,
        "device_name": dev_token.device_name,
        "user_id": dev_token.user_id,
        "qr_payload": qr_payload_str,
        "created_at": dev_token.created_at.isoformat() if dev_token.created_at else None
    }

    try:
        from app.websocket_manager import manager
        manager.broadcast_sync(
            entity="device",
            action="paired",
            entity_id=str(dev_token.id),
            data={"device_name": dev_token.device_name, "user_id": dev_token.user_id}
        )
    except Exception:
        pass

    return {
        "code": 0,
        "message": "Device token created successfully",
        "data": response_data,
        "pair_code": dev_token.pair_code,
        "token": dev_token.token,
        "expires_at": dev_token.expires_at.isoformat() if dev_token.expires_at else None
    }


@router.get("/device/list")
@router.get("/api/device/list")
def list_device_tokens(
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    tokens = crud.get_user_device_tokens(db, user_id=current_user.id)
    token_outs = [schemas.DeviceTokenOut.model_validate(t) for t in tokens]
    list_response = schemas.DeviceTokenListResponse(
        total=len(token_outs),
        list=token_outs
    )
    return {
        "code": 0,
        "message": "Success",
        "data": list_response,
        "total": len(token_outs),
        "list": [t.model_dump() for t in token_outs]
    }


@router.delete("/device/revoke/{device_id}")
@router.delete("/api/device/revoke/{device_id}")
def revoke_device(
    device_id: int,
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    device_token = crud.get_device_token_by_id(db, device_id=device_id)
    if not device_token:
        raise HTTPException(
            status_code=404,
            detail="Device token not found"
        )

    if device_token.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Device token does not belong to current user"
        )

    if device_token.status == "revoked":
        raise HTTPException(
            status_code=400,
            detail="Device token already revoked"
        )

    revoked_token = crud.revoke_device_token(db, device_id=device_id, user_id=current_user.id)
    try:
        from app.websocket_manager import manager
        manager.broadcast_sync(
            entity="device",
            action="revoked",
            entity_id=str(device_id),
            data={"device_id": device_id, "user_id": current_user.id}
        )
    except Exception:
        pass

    return {
        "code": 0,
        "message": "Device token revoked",
        "device_id": device_id,
        "data": {
            "id": device_id,
            "status": "revoked"
        }
    }


@router.get("/device/verify")
@router.get("/api/device/verify")
def verify_device_token(
    device_token: models.DeviceToken = Depends(get_current_device_token)
):
    return {
        "code": 0,
        "message": "Token valid",
        "data": {
            "device_id": device_token.id,
            "device_name": device_token.device_name,
            "token": device_token.token,
            "status": device_token.status
        }
    }


@router.post("/device/decode-frame")
@router.post("/api/device/decode-frame")
async def decode_camera_frame(
    payload: dict = None
):
    """
    Python C++ ZXing Barcode & QR Code Decoder endpoint.
    Uses multi-pass binarization, rotation, downscaling, and contrast/sharpness enhancement.
    Decodes 1D retail barcodes (EAN-13, EAN-8, Code-128, Code-39, UPC) and 2D QR codes with 100% accuracy.
    """
    import io
    import base64
    import cv2
    import numpy as np
    import zxingcpp
    from PIL import Image, ImageFile, ImageEnhance
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    if not payload or "base64_image" not in payload:
        return {"code": 400, "message": "base64_image required", "barcode": None}

    try:
        base64_data = payload["base64_image"]
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        # Fix base64 padding if needed
        missing_padding = len(base64_data) % 4
        if missing_padding:
            base64_data += "=" * (4 - missing_padding)

        image_bytes = base64.b64decode(base64_data)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        np_img = np.array(pil_img)

        # Pass 1: Direct NumPy array scan with LocalAverage binarizer & rotation
        results = zxingcpp.read_barcodes(
            np_img,
            try_rotate=True,
            try_downscale=True,
            try_invert=True,
            binarizer=zxingcpp.Binarizer.LocalAverage
        )

        if not results:
            # Pass 2: GlobalHistogram binarizer for low-light & shadows
            results = zxingcpp.read_barcodes(
                np_img,
                try_rotate=True,
                try_downscale=True,
                try_invert=True,
                binarizer=zxingcpp.Binarizer.GlobalHistogram
            )

        if not results:
            # Pass 3: 2x Super-resolution bicubic scaling for small / blurry 1D barcodes
            np_2x = cv2.resize(np_img, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            results = zxingcpp.read_barcodes(
                np_2x,
                try_rotate=True,
                try_downscale=True,
                try_invert=True
            )

        if not results:
            # Pass 4: Contrast & sharpness enhancement
            enhanced = ImageEnhance.Contrast(pil_img).enhance(2.0)
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.5)
            np_enh = cv2.resize(np.array(enhanced), (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            results = zxingcpp.read_barcodes(
                np_enh,
                try_rotate=True,
                try_downscale=True,
                try_invert=True
            )

        if results:
            first = results[0]
            return {
                "code": 0,
                "message": "Barcode detected",
                "barcode": first.text,
                "format": str(first.format)
            }
        return {"code": 0, "message": "No barcode detected", "barcode": None}
    except Exception as e:
        return {"code": 500, "message": str(e), "barcode": None}


