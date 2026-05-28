from pathlib import Path

from tortoise import Tortoise
from config import Config


def ensure_sqlite_parent_dir(db_url: str) -> None:
    if not db_url.startswith("sqlite://"):
        return

    filename = db_url.removeprefix("sqlite://")
    if filename in {"", ":memory:"}:
        return

    parent = Path(filename).expanduser().parent
    if str(parent) != ".":
        parent.mkdir(parents=True, exist_ok=True)


async def init_db():
    ensure_sqlite_parent_dir(Config.DATABASE_URL)
    await Tortoise.init(
        db_url=Config.DATABASE_URL,
        modules={'models': ['models.user', 'models.board_game']},
    )
    await Tortoise.generate_schemas()
    await ensure_inline_message_columns()


async def ensure_inline_message_columns() -> None:
    connection = Tortoise.get_connection("default")
    is_sqlite = Config.DATABASE_URL.startswith("sqlite://")
    for table in ("chessgame", "checkersgame"):
        try:
            if is_sqlite:
                await connection.execute_script(
                    f'ALTER TABLE "{table}" ADD COLUMN "inline_message_id" VARCHAR(255);'
                )
            else:
                await connection.execute_script(
                    f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "inline_message_id" VARCHAR(255);'
                )
        except Exception as exc:
            message = str(exc).lower()
            if "duplicate column" not in message and "already exists" not in message:
                raise
