from openai import OpenAI
from dotenv import load_dotenv

from gitsource import GithubRepositoryDataReader
from minsearch import Index

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult
)

import sqlite3

load_dotenv()


# -----------------------------
# SQLite Exporter
# -----------------------------

class SQLiteSpanExporter(SpanExporter):

    def __init__(self, db_path="traces.db"):
        self.conn = sqlite3.connect(db_path)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                name TEXT,
                start_time INTEGER,
                end_time INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost REAL
            )
        """)

        self.conn.commit()

    def export(self, spans):
        for span in spans:
            attrs = dict(span.attributes or {})

            self.conn.execute(
                "INSERT INTO spans VALUES (?, ?, ?, ?, ?, ?)",
                (
                    span.name,
                    span.start_time,
                    span.end_time,
                    attrs.get("input_tokens"),
                    attrs.get("output_tokens"),
                    attrs.get("cost"),
                ),
            )

        self.conn.commit()

        return SpanExportResult.SUCCESS

    def shutdown(self):
        self.conn.close()

    def force_flush(self):
        return True


# -----------------------------
# OpenTelemetry setup
# -----------------------------

provider = TracerProvider()

provider.add_span_processor(
    SimpleSpanProcessor(
        SQLiteSpanExporter("traces.db")
    )
)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp")


# -----------------------------
# RAG setup
# -----------------------------

from rag_helper import RAGBase


COMMIT = "8c1834d"


reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id=COMMIT,
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)

documents = [file.parse() for file in reader.read()]


index = Index(
    text_fields=["content"],
    keyword_fields=["filename"]
)

index.fit(documents)


client = OpenAI()


# -----------------------------
# Traced RAG
# -----------------------------

class RAGTraced(RAGBase):

    def rag(self, query):
        with tracer.start_as_current_span("rag"):
            return super().rag(query)


    def search(self, query):
        with tracer.start_as_current_span("search"):
            return super().search(query)


    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:

            response = super().llm(prompt)

            usage = response.usage

            span.set_attribute(
                "input_tokens",
                usage.input_tokens
            )

            span.set_attribute(
                "output_tokens",
                usage.output_tokens
            )

            return response