from ..cw.ContentWarningNames import ContentWarningNames
from fastapi import APIRouter

get_names_router = APIRouter()


@get_names_router.get("/names")
def get_all_cw_names():
    """
    Returns an ordered list of CW names/types
    """

    return {"cws": [name.value for name in ContentWarningNames]}
