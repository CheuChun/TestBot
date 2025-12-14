from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User

DATABASE_URL = "sqlite+aiosqlite:///./bot_users.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)

async def add_user(user_id: int, paid: bool = False, model: str = "meta-llama/llama-3.3-70b-instruct:free"):
    async with async_session() as session:
        user = User(id=user_id, paid=paid, current_model=model, history={})
        session.add(user)
        await session.commit()

async def update_user(user: User):
    async with async_session() as session:
        await session.merge(user)
        await session.commit()
