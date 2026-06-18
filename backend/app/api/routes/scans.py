from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.plans import enforce_scan_quota
from ...models.scan import Scan
from ...models.user import User
from ...schemas.scan import ScanOut
from ...services.scanning import execute_scan, start_scan
from ..deps import get_current_user

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("", response_model=ScanOut, status_code=202)
def trigger_scan(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Queue a scan across the user's plan-allowed connectors.

    Returns immediately with a ``pending`` scan; the network-bound work runs in a
    background task. Poll ``GET /scans/{id}`` until ``status == 'completed'``.
    """
    enforce_scan_quota(db, current_user)  # 429 when the plan's daily limit is hit
    scan = start_scan(db, current_user, trigger="manual")
    background_tasks.add_task(execute_scan, scan.id)
    return scan


@router.get("", response_model=list[ScanOut])
def list_scans(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.started_at.desc())
        .limit(limit)
    ).all()


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scan = db.get(Scan, scan_id)
    if not scan or scan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
