from ..databases.ContentWarningTable import ContentWarningTable
from .ContentWarning import ContentWarningReduced
from fastapi import APIRouter, HTTPException, status
from typing import Union

get_cw_router = APIRouter()


@get_cw_router.get("/cw/{id}")
def get_cw(id: str) -> Union[ContentWarningReduced, None]:
    warning = ContentWarningTable.get_warning(id)

    if warning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"CW {id} does not exist."
        )

    return warning.to_ContentWarningReduced()
