# import asyncio
# from typing import Any

# from fastapi import APIRouter, Depends
# from loguru import logger
# from sqlalchemy import select
# from qdrant_client import QdrantClient
# from upstash_redis import Redis
# from groq import AsyncGroq

# from app.config import get_settings
# from app.db.session import SessionLocal
# from app.middleware.auth import User, require_admin
# from app.services.query_cache_service import query_cache
# from app.services.web_search import search_web

# router = APIRouter(tags=["admin"])
# settings = get_settings()


# async def _ping_postgres() -> bool:
#     try:
#         async with SessionLocal() as session:
#             await session.execute(select(1))
#         return True
#     except Exception as exc:
#         logger.debug("Postgres health check failed: {}", exc)
#         return False


# async def _ping_qdrant() -> bool:
#     try:
#         def _check() -> None:
#             client = QdrantClient(url=settings.QDRANT_URL, timeout=2)
#             client.get_collections()

#         await asyncio.to_thread(_check)
#         return True
#     except Exception as exc:
#         logger.debug("Qdrant health check failed: {}", exc)
#         return False


# async def _ping_redis() -> bool:
#     try:
#         def _check() -> None:
#             redis = Redis(url=settings.UPSTASH_REDIS_URL, token=settings.UPSTASH_REDIS_TOKEN)
#             redis.ping()

#         await asyncio.to_thread(_check)
#         return True
#     except Exception as exc:
#         logger.debug("Redis health check failed: {}", exc)
#         return False


# async def _ping_groq() -> bool:
#     try:
#         client = AsyncGroq(api_key = settings.GROQ_API_KEY, timeout = 3.0)
#         await client.models.list()
#         return True
#     except Exception as exc:
#         logger.debug("Groq health check failed: {}", exc)
#         return False


# async def _ping_tavily() -> bool:
#     try:
#         await asyncio.to_thread(search_web, "health check")
#         return True
#     except ValueError:
#         # Tavily key not configured — still "up" if the module loads
#         return True
#     except Exception as exc:
#         logger.debug("Tavily health check failed: {}", exc)
#         return False


# @router.get("/admin/health")
# async def health_check() -> dict[str, Any]:
#     results = await asyncio.gather(
#         asyncio.wait_for(_ping_postgres(), timeout=3.0),
#         asyncio.wait_for(_ping_qdrant(), timeout=3.0),
#         asyncio.wait_for(_ping_redis(), timeout=3.0),
#         asyncio.wait_for(_ping_groq(), timeout=4.0),
#         asyncio.wait_for(_ping_tavily(), timeout=4.0),
#         return_exceptions=True,
#     )
#     postgres_ok = results[0] is True
#     qdrant_ok = results[1] is True
#     redis_ok = results[2] is True
#     groq_ok = results[3] is True
#     tavily_ok = results[4] is True

#     all_ok = postgres_ok and qdrant_ok and redis_ok and groq_ok and tavily_ok
#     status = "ok" if all_ok else "degraded"

#     return {
#         "status": status,
#         "qdrant": qdrant_ok,
#         "postgres": postgres_ok,
#         "redis": redis_ok,
#         "groq": groq_ok,
#         "tavily": tavily_ok,
#     }


# @router.get("/admin/cache/stats")
# async def cache_stats(user: User = Depends(require_admin)) -> dict[str, Any]:
#     """Return per-cache hit/miss/set counts."""
#     raw = query_cache.stats()

#     def _tier(name: str) -> dict[str, int | float]:
#         tier_data = raw.get(name, {})
#         return {
#             "hits": int(tier_data.get("hits", 0)),
#             "misses": int(tier_data.get("misses", 0)),
#             "sets": int(tier_data.get("sets", 0)),
#             "hit_rate": float(tier_data.get("hit_rate", 0.0)),
#         }

#     return {
#         "embedding": _tier("embedding"),
#         "rag": _tier("rag_answer"),
#         "sql_gen": _tier("sql_gen"),
#         "sql_result": _tier("sql_result"),
#         "intent_router": _tier("intent"),
#     }


# @router.post("/admin/cache/clear")
# async def cache_clear(user: User = Depends(require_admin)) -> dict[str, Any]:
#     """Clear all caches (Redis + in-memory)."""
#     cleared = query_cache.clear()
#     return {"status": "ok", "cleared": cleared}