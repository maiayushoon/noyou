from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.plans import get_limits
from ...models.account import Account
from ...models.user import User
from ...schemas.account import AccountCreate, AccountOut
from ..deps import get_current_user

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.scalars(select(Account).where(Account.user_id == current_user.id)).all()


@router.post("", response_model=AccountOut, status_code=201)
def add_account(
    payload: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Enforce the plan's monitored-identity limit (-1 == unlimited).
    limit = get_limits(current_user.plan)["max_accounts"]
    if limit != -1:
        current = db.scalar(
            select(func.count()).select_from(Account).where(Account.user_id == current_user.id)
        ) or 0
        if current >= limit:
            raise HTTPException(
                status_code=402,
                detail=f"Your plan allows {limit} monitored identit{'y' if limit == 1 else 'ies'}. Upgrade to add more.",
            )

    account = Account(
        user_id=current_user.id,
        platform=payload.platform.lower(),
        handle=payload.handle,
        display_name=payload.display_name,
        profile_url=payload.profile_url,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=204)
def remove_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.get(Account, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
