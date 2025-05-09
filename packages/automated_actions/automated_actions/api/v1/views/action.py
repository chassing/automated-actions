import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from automated_actions.api.v1.dependencies import UserDep
from automated_actions.db.models import (
    ActionSchemaOut,
    ActionStatus,
)
from automated_actions.db.models._action import ActionManager, get_action_manager

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/actions", operation_id="action-list")
def action_list(
    user: UserDep,
    action_mgr: Annotated[ActionManager, Depends(get_action_manager)],
    status: Annotated[ActionStatus | None, Query()] = ActionStatus.RUNNING,
) -> list[ActionSchemaOut]:
    """List all user actions."""
    status = status or ActionStatus.RUNNING
    return [action.dump() for action in action_mgr.get_user_actions(user.email, status)]


@router.get("/actions/{action_id}", operation_id="action-detail")
def action_detail(
    action_id: str, action_mgr: Annotated[ActionManager, Depends(get_action_manager)]
) -> ActionSchemaOut:
    """Retrieve an action."""
    return action_mgr.get_or_404(action_id).dump()


@router.post("/actions/{action_id}", operation_id="action-cancel", status_code=202)
def action_cancel(
    action_id: str, action_mgr: Annotated[ActionManager, Depends(get_action_manager)]
) -> ActionSchemaOut:
    """Cancel an action."""
    action = action_mgr.get_or_404(action_id)
    action.set_status(ActionStatus.CANCELLED)
    return action.dump()
