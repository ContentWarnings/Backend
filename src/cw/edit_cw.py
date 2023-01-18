# References
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
# https://fastapi.tiangolo.com/tutorial/handling-errors/

from ..databases.MovieTable import MovieTable
from ..databases.ContentWarningTable import ContentWarningTable
from .ContentWarning import ContentWarningReduced, Nothing
from fastapi import APIRouter, status, HTTPException
from typing import Union

edit_cw_router = APIRouter()


@edit_cw_router.post("/cw/{cw_id}")
def edit_cw(
    cw_id: str, root: Union[ContentWarningReduced, Nothing]
) -> ContentWarningReduced:
    cw = ContentWarningTable.get_warning(cw_id)
    if cw is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no cw exists with id {cw_id}",
        )

    # if JSON body is passed in empty, we are to delete cw from CW table and
    # movies table, returning appropriate JSON on results
    if type(root) is Nothing:
        res1 = MovieTable.delete_warning_from_movie(cw.movie_id, cw.id)
        res2 = ContentWarningTable.delete_warning(cw_id)
        res1.update(res2)
        return res1

    # if JSON body is a valid cw, we edit it
    result = ContentWarningTable.edit_warning(root.to_ContentWarning())
    if type(result) is tuple:
        raise HTTPException(status_code=result[0], detail=result[1])
    return result.to_ContentWarningReduced().jsonify()
