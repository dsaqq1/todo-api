import pytest
import src.database as database


@pytest.mark.asyncio
async def test_get_pool_raises_when_not_initialized(monkeypatch):
    monkeypatch.setattr(database, "_pool", None)

    with pytest.raises(RuntimeError, match="not initialized"):
        await database.get_pool()
