from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.models import Base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Jadvallarni yaratadi va eski jadvallarga yangi ustunlarni qo'shadi (migratsiya)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Yangi qo'shilgan ustunlarni eski jadvalga xavfsiz qo'shib qo'yamiz
        migrations = [
            "ALTER TABLE movies ADD COLUMN IF NOT EXISTS channel_message_id INTEGER",
        ]
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception as e:
                print(f"⚠️ Migratsiya xatosi (e'tiborsiz qoldirildi): {e}")
