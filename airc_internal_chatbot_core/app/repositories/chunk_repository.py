"""
Chunk Repository - Data access cho text chunks
"""
from typing import List, Optional

from sqlalchemy import and_, delete, or_, select

from app.models.orm import Chunk
from app.repositories.base_repository import BaseRepository


def _ilike_pattern(word: str) -> str:
    escaped = word.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class ChunkRepository(BaseRepository):
    """Repository cho Chunk operations"""

    def __init__(self, session):
        super().__init__(session)

    def _build_chunk(
        self,
        dataset_id,
        dataset_file_id,
        file_id,
        chunk: dict,
        is_parent: bool = False,
        parent_chunk_id=None,
    ) -> Chunk:
        extra = {}
        if chunk.get("vector_id") is not None:
            extra["vector_id"] = chunk.get("vector_id")
        if chunk.get("row_range") is not None:
            extra["row_range"] = chunk.get("row_range")
        return Chunk(
            dataset_id=dataset_id,
            dataset_file_id=dataset_file_id,
            file_id=file_id,
            chunk_index=chunk.get("chunk_index", 0),
            text=chunk.get("text") or "",
            embedding_text=chunk.get("embedding_text"),
            context_enriched_text=chunk.get("context_enriched_text", chunk.get("text")),
            heading_path=chunk.get("heading_path") or [],
            is_parent=is_parent,
            parent_chunk_id=parent_chunk_id,
            domain=chunk.get("domain", "general"),
            language=chunk.get("language", "vi"),
            section_type=chunk.get("section_type", "plain"),
            chunk_role=chunk.get("chunk_role", "parent" if is_parent else ("child" if parent_chunk_id else "standalone")),
            is_table=bool(chunk.get("is_table", False)),
            table_caption=chunk.get("table_caption"),
            table_header=chunk.get("table_header") or [],
            quality_flags=chunk.get("quality_flags") or [],
            page=chunk.get("page"),
            extra=extra,
            qdrant_point_id=str(chunk["vector_id"]) if chunk.get("vector_id") is not None else None,
        )

    async def create_chunk(
        self,
        dataset_id: str,
        dataset_file_id: str,
        file_id: str,
        chunk_index: int,
        text: str,
        vector_id: Optional[int] = None,
    ) -> dict:
        ds_id = self.parse_id(dataset_id)
        df_id = self.parse_id(dataset_file_id)
        f_id = self.parse_id(file_id)
        row = Chunk(
            dataset_id=ds_id,
            dataset_file_id=df_id,
            file_id=f_id,
            chunk_index=chunk_index,
            text=text,
            extra={"vector_id": vector_id} if vector_id is not None else {},
            qdrant_point_id=str(vector_id) if vector_id is not None else None,
        )
        self.session.add(row)
        await self.session.flush()
        return self.serialize_row(row)

    async def create_chunks(
        self,
        dataset_id: str,
        dataset_file_id: str,
        file_id: str,
        texts: List[str] = None,
        vectors: List[List[float]] = None,
        chunks_data: List[dict] = None,
    ) -> List[str]:
        ds_id = self.parse_id(dataset_id)
        df_id = self.parse_id(dataset_file_id)
        f_id = self.parse_id(file_id)
        rows = []
        if chunks_data:
            for chunk in chunks_data:
                rows.append(
                    self._build_chunk(
                        ds_id,
                        df_id,
                        f_id,
                        chunk,
                        is_parent=bool(chunk.get("is_parent", False)),
                        parent_chunk_id=self.parse_id(chunk["parent_chunk_id"]) if chunk.get("parent_chunk_id") else None,
                    )
                )
        else:
            for i, text in enumerate(texts or []):
                rows.append(
                    self._build_chunk(
                        ds_id,
                        df_id,
                        f_id,
                        {"chunk_index": i, "text": text, "embedding_text": text, "context_enriched_text": text},
                    )
                )
        if not rows:
            return []
        self.session.add_all(rows)
        await self.session.flush()
        return [str(row.id) for row in rows]

    async def get_parent_chunks_by_ids(self, parent_ids: List[str]) -> List[dict]:
        uids = [uid for uid in (self.parse_id(pid) for pid in parent_ids if pid) if uid]
        if not uids:
            return []
        result = await self.session.execute(select(Chunk).where(Chunk.id.in_(uids)))
        return self.serialize_rows(result.scalars().all())

    async def create_chunks_advanced(
        self,
        dataset_id: str,
        dataset_file_id: str,
        file_id: str,
        chunks: List[dict],
    ) -> List[dict]:
        if not chunks:
            return []
        ds_id = self.parse_id(dataset_id)
        df_id = self.parse_id(dataset_file_id)
        f_id = self.parse_id(file_id)

        parent_chunks = [c for c in chunks if c.get("is_parent") is True]
        parent_map = {}
        for p_chunk in parent_chunks:
            row = self._build_chunk(ds_id, df_id, f_id, p_chunk, is_parent=True)
            self.session.add(row)
            await self.session.flush()
            p_chunk["id"] = str(row.id)
            parent_map[p_chunk["chunk_index"]] = row.id

        other_chunks = [c for c in chunks if not c.get("is_parent")]
        for c_chunk in other_chunks:
            p_idx = c_chunk.get("parent_chunk_index")
            p_id = parent_map.get(p_idx) if p_idx is not None else None
            row = self._build_chunk(ds_id, df_id, f_id, c_chunk, is_parent=False, parent_chunk_id=p_id)
            self.session.add(row)
            await self.session.flush()
            c_chunk["id"] = str(row.id)
            c_chunk["parent_chunk_id"] = str(p_id) if p_id else None
        return chunks

    _KEYWORD_STOPWORDS = {
        "hãy", "về", "của", "là", "và", "cho", "trong", "một", "các", "này",
        "được", "có", "không", "tôi", "bạn", "anh", "chị", "câu", "hỏi",
        "xin", "vui", "lòng", "thì", "nếu", "như", "với", "tại", "đó",
        "đây", "khi", "để", "hay", "hoặc", "gì", "nào", "ai", "rằng",
        "the", "a", "an", "of", "to", "in", "on", "for", "is", "are",
        "please", "tell", "me", "about",
    }

    async def search_by_text(
        self,
        query: str,
        dataset_file_ids: List[str],
        limit: int = 5,
    ) -> List[dict]:
        raw_words = [w.strip(".,?!:;\"'()[]") for w in query.strip().split()]
        keywords = [
            w for w in raw_words
            if len(w) > 1 and w.lower() not in self._KEYWORD_STOPWORDS
        ]
        if not keywords:
            keywords = [w for w in raw_words if len(w) > 1] or [query.strip()]
        if not keywords or not any(keywords):
            return []

        ids = [uid for uid in (self.parse_id(i) for i in dataset_file_ids) if uid]
        if not ids:
            return []

        and_conditions = [Chunk.text.ilike(_ilike_pattern(word)) for word in keywords]
        result = await self.session.execute(
            select(Chunk).where(Chunk.dataset_file_id.in_(ids), and_(*and_conditions)).limit(limit)
        )
        docs = self.serialize_rows(result.scalars().all())
        if docs:
            return docs

        or_words = [w for w in keywords if len(w) >= 3]
        if not or_words:
            return []
        or_conditions = [Chunk.text.ilike(_ilike_pattern(word)) for word in or_words]
        result = await self.session.execute(
            select(Chunk).where(Chunk.dataset_file_id.in_(ids), or_(*or_conditions)).limit(limit)
        )
        return self.serialize_rows(result.scalars().all())

    async def get_by_dataset_file(self, dataset_id: str, dataset_file_id: str) -> List[dict]:
        ds_id = self.parse_id(dataset_id)
        df_id = self.parse_id(dataset_file_id)
        if not ds_id or not df_id:
            return []
        result = await self.session.execute(
            select(Chunk)
            .where(Chunk.dataset_id == ds_id, Chunk.dataset_file_id == df_id)
            .order_by(Chunk.chunk_index.asc())
        )
        return self.serialize_rows(result.scalars().all())

    async def get_by_ids(self, chunk_ids: List[str]) -> List[dict]:
        uids = [uid for uid in (self.parse_id(cid) for cid in chunk_ids) if uid]
        if not uids:
            return []
        result = await self.session.execute(select(Chunk).where(Chunk.id.in_(uids)))
        return self.serialize_rows(result.scalars().all())

    async def get_by_vector_ids(
        self,
        dataset_id: str,
        vector_ids: List[int],
        enabled_df_ids: List[str],
    ) -> List[dict]:
        ds_id = self.parse_id(dataset_id)
        df_ids = [uid for uid in (self.parse_id(i) for i in enabled_df_ids) if uid]
        if not ds_id or not df_ids or not vector_ids:
            return []
        point_ids = [str(v) for v in vector_ids]
        result = await self.session.execute(
            select(Chunk).where(
                Chunk.dataset_id == ds_id,
                Chunk.dataset_file_id.in_(df_ids),
                Chunk.qdrant_point_id.in_(point_ids),
            )
        )
        return self.serialize_rows(result.scalars().all())

    async def update_vector_id(self, chunk_id: str, vector_id: int) -> bool:
        uid = self.parse_id(chunk_id)
        if not uid:
            return False
        row = await self.session.get(Chunk, uid)
        if not row:
            return False
        extra = dict(row.extra or {})
        extra["vector_id"] = vector_id
        row.extra = extra
        row.qdrant_point_id = str(vector_id)
        await self.session.flush()
        return True

    async def delete_by_dataset_file(self, dataset_id: str, dataset_file_id: str) -> int:
        ds_id = self.parse_id(dataset_id)
        df_id = self.parse_id(dataset_file_id)
        if not ds_id or not df_id:
            return 0
        result = await self.session.execute(
            delete(Chunk).where(Chunk.dataset_id == ds_id, Chunk.dataset_file_id == df_id)
        )
        return result.rowcount or 0

    async def delete_by_dataset(self, dataset_id: str) -> int:
        uid = self.parse_id(dataset_id)
        if not uid:
            return 0
        result = await self.session.execute(delete(Chunk).where(Chunk.dataset_id == uid))
        return result.rowcount or 0
