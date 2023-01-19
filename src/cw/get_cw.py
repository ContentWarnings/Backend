from ..databases.ContentWarningTable import ContentWarningTable
from .ContentWarning import ContentWarningReduced
from fastapi import APIRouter
from typing import Union

get_cw_router = APIRouter()


@get_cw_router.get("/cw/{id}")
def get_cw(id: str) -> Union[ContentWarningReduced, None]:
    warning = ContentWarningTable.get_warning(id)
    return warning if warning is None else warning.to_ContentWarningReduced()
