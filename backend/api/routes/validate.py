"""Constitution validation endpoint supporting both file upload and raw content."""

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from backend.sdk.engine import Engine

router = APIRouter()


@router.post(
    "/validate",
    summary="Validate a Constitution",
    description="Upload a YAML/JSON constitution file or post raw content to validate its structure without loading it into the engine.",
)
async def validate_constitution(
    request: Request,
    file: UploadFile | None = File(default=None),
) -> dict[str, str]:
    """Validate a constitution structure."""
    content = b""
    filename = "constitution.yaml"

    if file:
        content = await file.read()
        filename = file.filename or "uploaded.yaml"
    else:
        content = await request.body()

    if not content:
        raise HTTPException(status_code=400, detail="Empty constitution payload")

    suffix = ".yaml" if filename.endswith(".yaml") else ".json"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        tmp.write(content)

    try:
        is_valid = Engine.validate_constitution(tmp_path)
        return {"status": "valid" if is_valid else "invalid", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid constitution: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
