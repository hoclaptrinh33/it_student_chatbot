"""VectorService.search passes course_id Qdrant filter when given."""
import sys
from types import ModuleType
from unittest.mock import MagicMock

import numpy as np


def _install_qdrant_stub():
    try:
        import qdrant_client  # noqa: F401
        return
    except ImportError:
        pass

    class FieldCondition:
        def __init__(self, key, match):
            self.key = key
            self.match = match

    class MatchValue:
        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            return isinstance(other, MatchValue) and self.value == other.value

    class MatchAny:
        def __init__(self, any):
            self.any = any

    class Filter:
        def __init__(self, must=None):
            self.must = must or []

    class FilterSelector:
        def __init__(self, filter=None):
            self.filter = filter

    class PayloadSchemaType:
        KEYWORD = "keyword"

    class Distance:
        COSINE = "Cosine"

    class VectorParams:
        def __init__(self, size, distance):
            self.size = size
            self.distance = distance

    class PointStruct:
        def __init__(self, id, vector, payload):
            self.id = id
            self.vector = vector
            self.payload = payload

    models = ModuleType("qdrant_client.http.models")
    models.FieldCondition = FieldCondition
    models.MatchValue = MatchValue
    models.MatchAny = MatchAny
    models.Filter = Filter
    models.FilterSelector = FilterSelector
    models.PayloadSchemaType = PayloadSchemaType
    models.Distance = Distance
    models.VectorParams = VectorParams
    models.PointStruct = PointStruct

    http = ModuleType("qdrant_client.http")
    http.models = models

    client_mod = ModuleType("qdrant_client")
    client_mod.QdrantClient = MagicMock
    client_mod.http = http

    sys.modules["qdrant_client"] = client_mod
    sys.modules["qdrant_client.http"] = http
    sys.modules["qdrant_client.http.models"] = models


_install_qdrant_stub()

from qdrant_client.http import models as rest  # noqa: E402
from app.services.vector_service import VectorService  # noqa: E402

COURSE_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def _collection(name: str):
    coll = MagicMock()
    coll.name = name
    return coll


def _hit(payload=None):
    hit = MagicMock()
    hit.score = 0.91
    hit.payload = payload or {"chunk_id": "c1", "course_id": COURSE_ID}
    return hit


def test_search_passes_course_id_filter_when_given():
    svc = VectorService()
    client = MagicMock()
    client.get_collections.return_value.collections = [_collection("dataset_ds1")]
    client.query_points.return_value.points = [_hit()]
    svc._client = client

    scores, payloads = svc.search(
        "ds1",
        np.array([0.1, 0.2, 0.3]),
        top_k=5,
        course_id=COURSE_ID,
    )

    assert scores == [0.91]
    assert payloads[0]["course_id"] == COURSE_ID
    kwargs = client.query_points.call_args_list[0].kwargs
    query_filter = kwargs["query_filter"]
    assert query_filter is not None
    course_conds = [cond for cond in query_filter.must if getattr(cond, "key", None) == "course_id"]
    assert len(course_conds) == 1
    assert course_conds[0].match.value == COURSE_ID


def test_search_omits_course_id_filter_when_missing():
    svc = VectorService()
    client = MagicMock()
    client.get_collections.return_value.collections = [_collection("dataset_ds1")]
    client.query_points.return_value.points = [_hit()]
    svc._client = client

    svc.search("ds1", np.array([0.1, 0.2, 0.3]), top_k=3)
    kwargs = client.query_points.call_args.kwargs
    assert kwargs["query_filter"] is None


def test_ensure_collection_creates_course_id_keyword_index():
    svc = VectorService()
    client = MagicMock()
    client.get_collections.return_value.collections = []
    svc._client = client

    svc._ensure_collection("dataset_ds1", 768)

    client.create_collection.assert_called_once()
    index_kwargs = client.create_payload_index.call_args.kwargs
    assert index_kwargs["collection_name"] == "dataset_ds1"
    assert index_kwargs["field_name"] == "course_id"
    assert index_kwargs["field_schema"] == rest.PayloadSchemaType.KEYWORD
