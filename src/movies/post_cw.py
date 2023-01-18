# References
# https://fastapi.tiangolo.com/advanced/response-change-status-code/
# https://stackoverflow.com/questions/3825990/http-response-code-for-post-when-resource-already-exists

import boto3
from fastapi import Response, status
from ..cw.ContentWarning import ContentWarningReduced
from ..databases.ContentWarningTable import ContentWarningTable
from ..databases.MovieTable import MovieTable
from fastapi import APIRouter
from typing import Dict, List

post_cw_router = APIRouter()
dynamodb_client = boto3.client("dynamodb")


@post_cw_router.post("/movie/{id}")
def post_cw(
    id: int, root: ContentWarningReduced, response: Response
) -> Dict[ContentWarningReduced, Dict[str, str]]:
    # add cw to CW table
    result = ContentWarningTable.add_warning(root.to_ContentWarning())
    if type(result) is dict:
        response.status_code = status.HTTP_409_CONFLICT
        return result

    # add cw UUID to appropriate movie, creating entry if not inside movie table
    cw_ids: List[str] = MovieTable.add_warning_to_movie(id, root.id)

    retval_cw_list: List[dict] = []
    for cw_id in cw_ids:
        warning = ContentWarningTable.get_warning(cw_id)
        if warning is not None:
            retval_cw_list.append(warning.to_ContentWarningReduced().jsonify())

    return retval_cw_list
