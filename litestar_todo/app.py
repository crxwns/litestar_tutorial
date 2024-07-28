"""Main Application."""

import logging

import msgspec
from litestar import Litestar, Request, Response, get, post, put
from litestar.exceptions import HTTPException, NotFoundException
from litestar.exceptions.responses import create_exception_response  # type: ignore[reportUnknownVariableType]
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin, SwaggerRenderPlugin

logger = logging.getLogger(__name__)


class TodoItem(msgspec.Struct):
    """Todo item Struct."""

    title: str
    done: bool


TODO_LIST: list[TodoItem] = [
    TodoItem(title="Start writing TODO list", done=True),
    TodoItem(title="???", done=False),
    TodoItem(title="Profit", done=False),
]


@get("/")
async def get_list(done: bool | None = None) -> list[TodoItem]:
    """Get Todo Items."""
    if done is None:
        return TODO_LIST
    return [item for item in TODO_LIST if item.done == done]


@post("/")
async def add_item(data: TodoItem) -> list[TodoItem]:
    """Add TodoItem."""
    TODO_LIST.append(data)
    return TODO_LIST


def get_todo_by_title(todo_title: str) -> TodoItem:
    """Get TodoItem by title."""
    for item in TODO_LIST:
        if item.title == todo_title:
            return item
    raise NotFoundException(detail=f"TODO {todo_title!r} not found.")


@put("/{todo_title:str}")
async def update_item(todo_title: str, data: TodoItem) -> list[TodoItem]:
    """Update TodoItem."""
    todo_item = get_todo_by_title(todo_title=todo_title)
    todo_item.title = data.title
    todo_item.done = data.done
    return TODO_LIST


# Typing ignore shenanigans as I trust that litestar can handle his own request, exception and response types
def custom_exception(  # pyright: ignore[reportUnknownParameterType]
    req: Request,  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    exc: HTTPException,
) -> Response:  # pyright: ignore[reportMissingTypeArgument]
    """Global exception handler."""
    logger.warning(exc)
    return create_exception_response(req, exc)  # type: ignore[reportUnknownVariableType]


app = Litestar(
    route_handlers=[get_list, add_item, update_item],
    openapi_config=OpenAPIConfig(
        title="Example",
        description="Example OpenAPI",
        version="0.1.0",
        render_plugins=[ScalarRenderPlugin(), SwaggerRenderPlugin()],
    ),
    exception_handlers={HTTPException: custom_exception},
)
