from .DescriptionDict import DESCRIPTION_DICT
from ..cw.ContentWarningNames import ContentWarningNames
from fastapi import APIRouter

get_desc_router = APIRouter()


@get_desc_router.get("/descriptions")
def get_cw_name_description(name: ContentWarningNames):
    """
    Given a CW name, return description
    """
    return {"response": DESCRIPTION_DICT[ContentWarningNames(name)]}
