import os
import asyncio
import warnings

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

warnings.filterwarnings(
    "ignore",
    message=r".*Pydantic serializer warnings.*",
    category=UserWarning,
)

load_dotenv()

# =================================================
# PROVIDER SELECTION
# =================================================
#
# This is the ONLY switch you ever need to touch
# when changing models.
#
# .env:
#   LLM_PROVIDER=ollama   -> uses OLLAMA_MODEL
#   LLM_PROVIDER=openai   -> uses OPENAI_MODEL
#
# =================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
).lower()


# =================================================
# BUILD LLM
# =================================================

if LLM_PROVIDER == "openai":

    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-5"
        ),
        temperature=0,
    )

    print(
        f"🤖 LLM Provider: OpenAI "
        f"({os.getenv('OPENAI_MODEL', 'gpt-5')})"
    )


elif LLM_PROVIDER == "ollama":

    from langchain_ollama import ChatOllama

    _ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "gemma4:cloud"
    )

    _ollama_kwargs = dict(
        model=_ollama_model,
        temperature=0,

        # -------------------------------------------------
        # Give a generous output budget. Even with thinking
        # disabled, a large SupervisorPlan (many tasks,
        # nested arguments) needs real headroom — Ollama's
        # default num_predict can be too small and silently
        # truncate the JSON mid-object.
        # -------------------------------------------------

        num_predict=int(
            os.getenv(
                "OLLAMA_NUM_PREDICT",
                "4096"
            )
        ),

        # -------------------------------------------------
        # Ollama's default context window is only 2048
        # tokens per request unless explicitly set, even
        # if the underlying model supports far more. Raise
        # this to comfortably fit the full tool catalog +
        # instruction prompt.
        # -------------------------------------------------

        num_ctx=int(
            os.getenv(
                "OLLAMA_NUM_CTX",
                "16384"
            )
        ),

        # -------------------------------------------------
        # Keep the model resident in memory so repeated
        # requests don't trigger a cold "load" response
        # (which returns empty content and breaks JSON
        # parsing for structured output).
        # -------------------------------------------------

        keep_alive=os.getenv(
            "OLLAMA_KEEP_ALIVE",
            "30m"
        ),
    )

    # -----------------------------------------------------
    # This model reports a "thinking" capability (visible
    # via `ollama show`). Thinking models generate internal
    # reasoning tokens before the final answer. When
    # combined with structured/json-schema-constrained
    # output, the model can spend its entire output budget
    # on thinking and leave nothing for the actual JSON —
    # which shows up as an empty response (misreported by
    # langchain_ollama as done_reason='load').
    #
    # Disable thinking so the model goes straight to
    # producing the structured JSON output. Guarded in a
    # try/except because the `reasoning` kwarg is only
    # supported in newer langchain_ollama versions — if
    # it's missing, we fall back without it rather than
    # crashing at startup.
    # -----------------------------------------------------

    try:

        llm = ChatOllama(
            reasoning=False,
            **_ollama_kwargs,
        )

    except TypeError:

        print(
            "⚠️ Installed langchain_ollama version "
            "does not support the 'reasoning' "
            "parameter. Run: pip install -U "
            "langchain-ollama  to enable disabling "
            "thinking mode. Continuing without it."
        )

        llm = ChatOllama(
            **_ollama_kwargs
        )

    print(
        f"🤖 LLM Provider: Ollama "
        f"({os.getenv('OLLAMA_MODEL', 'gemma4:cloud')})"
    )


else:

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}"
    )


# =================================================
# BUILD EMBEDDINGS
# =================================================
#
# Same provider-agnostic pattern as the chat LLM
# above. RAG/vectorstore code should import
# `embeddings` from here instead of constructing
# OllamaEmbeddings / OpenAIEmbeddings directly, so
# switching LLM_PROVIDER in .env also switches the
# embedding model automatically — no other file ever
# needs to change.
#
# =================================================

if LLM_PROVIDER == "openai":

    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(
        model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small"
        ),
    )

    print(
        f"🧬 Embeddings Provider: OpenAI "
        f"({os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')})"
    )


elif LLM_PROVIDER == "ollama":

    from langchain_ollama import OllamaEmbeddings

    _ollama_embed_model = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text"
    )

    # -------------------------------------------------
    # Force CPU-only inference for embeddings.
    #
    # On GPUs with very limited VRAM (observed:
    # cudaMalloc failed / out-of-memory errors even for
    # a ~216MB buffer), the embedding model can fail to
    # load into GPU memory — especially if another
    # Ollama model is already resident there via
    # keep_alive. num_gpu=0 tells Ollama to run this
    # model entirely on CPU, sidestepping VRAM limits
    # completely. nomic-embed-text is small enough that
    # CPU inference for typical document chunk volumes
    # is fast and reliable.
    #
    # Guarded with try/except in case an older
    # langchain-ollama version doesn't expose num_gpu as
    # a constructor kwarg — falls back to default (GPU)
    # behavior rather than crashing at import time.
    # -------------------------------------------------

    try:

        embeddings = OllamaEmbeddings(
            model=_ollama_embed_model,
            num_gpu=0,
        )

    except TypeError:

        print(
            "⚠️ Installed langchain_ollama version "
            "does not support 'num_gpu' for "
            "OllamaEmbeddings. Falling back to "
            "default (GPU) behavior — if you hit "
            "CUDA out-of-memory errors during "
            "embedding, upgrade langchain-ollama or "
            "free up GPU memory."
        )

        embeddings = OllamaEmbeddings(
            model=_ollama_embed_model,
        )

    print(
        f"🧬 Embeddings Provider: Ollama "
        f"({_ollama_embed_model}, CPU-only)"
    )


else:

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}"
    )


# =================================================
# STRUCTURED OUTPUT HELPER
# =================================================
#
# Different providers need different structured-output
# strategies:
#
# - Ollama / most local models (Gemma, Llama, Mistral,
#   etc.) do NOT reliably support native function/tool
#   calling for structured output. They need
#   method="json_schema", which asks the model to
#   directly emit JSON matching the schema.
#
# - OpenAI models support native function calling,
#   which is the default and most reliable method
#   for them ("function_calling"). Forcing json_schema
#   is unnecessary and can even be slightly less
#   reliable on some OpenAI models.
#
# Every agent (supervisor, executor, risk analysis,
# etc.) should call get_structured_llm() instead of
# llm.with_structured_output() directly. This means
# NONE of your agent files ever need to know or care
# which provider is active.
#
# =================================================

def get_structured_llm(base_llm, schema):

    if LLM_PROVIDER == "ollama":

        return base_llm.with_structured_output(
            schema,
            method="json_schema",
        )

    # OpenAI (and any future provider that handles
    # native function-calling well) uses the default
    # method.

    return base_llm.with_structured_output(
        schema
    )


# =================================================
# PROVIDER-AWARE PROMPT MESSAGE
# =================================================
#
# Confirmed via testing: gemma4:cloud (Ollama) returns
# an empty response with done_reason='load' for ANY
# conversation that contains only a SystemMessage — no
# actual content is generated, regardless of prompt
# size or content. Sending the exact same prompt as a
# HumanMessage instead works reliably every time.
#
# OpenAI models don't have this problem — a lone
# HumanMessage works fine there too — but OpenAI is
# generally more reliable when instructions live in a
# proper SystemMessage separate from the "request",
# especially for long rule-heavy prompts like the
# supervisor's.
#
# This helper isolates that provider difference so
# agents never need to know or care which provider is
# active — same pattern as get_structured_llm().
#
# Usage:
#
#   messages = build_prompt_messages(prompt)
#   response = await llm.ainvoke(messages)
#
# =================================================

def build_prompt_messages(content):

    if LLM_PROVIDER == "ollama":

        return [
            HumanMessage(
                content=content
            )
        ]

    # OpenAI (and any future provider without this
    # quirk) uses a proper SystemMessage.

    return [
        SystemMessage(
            content=content
        )
    ]


# =================================================
# RETRY WRAPPER FOR STRUCTURED CALLS
# =================================================
#
# Cold-start Ollama models sometimes return an empty
# response on the very first call after being loaded
# into memory (done_reason='load' with no content).
# This causes a JSON parsing failure even though the
# model is otherwise working correctly.
#
# This wrapper retries the call a couple of times so
# a cold-start failure self-heals instead of failing
# the whole request. It's cheap to keep even once you
# switch to OpenAI, since a successful first attempt
# never triggers a retry.
#
# =================================================

async def call_structured_llm(
    structured_llm,
    messages,
    timeout=120,
    retries=2,
):

    last_error = None

    for attempt in range(1, retries + 2):

        try:

            return await asyncio.wait_for(
                structured_llm.ainvoke(
                    messages
                ),
                timeout=timeout,
            )

        except Exception as e:

            last_error = e

            print(
                f"\n⚠️ Structured LLM call "
                f"attempt {attempt} failed: {e}"
            )

            if attempt <= retries:

                print(
                    "🔁 Retrying "
                    "(model may have just "
                    "finished loading)..."
                )

                await asyncio.sleep(1)

    raise last_error


# =================================================
# LEAN TOOL SCHEMA
# =================================================
#
# Full Pydantic JSON schemas (via model_json_schema())
# include a lot of scaffolding that's irrelevant for
# an LLM prompt: $defs, title, additionalProperties,
# nested $ref indirection, etc. Across 38 tools this
# can bloat the prompt significantly and is a strong
# suspect when structured output consistently returns
# empty for local/cloud models with limited effective
# instruction-following at long context lengths.
#
# This produces a compact { name: {type, description,
# required} } representation per argument instead of
# the full raw schema. Agents building a tool catalog
# for a prompt should use this instead of dumping
# tool.args_schema.model_json_schema() directly.
#
# =================================================

def get_lean_tool_schema(tool):

    try:

        schema = getattr(
            tool,
            "args_schema",
            None
        )

        if not schema:
            return {}

        if hasattr(
            schema,
            "model_json_schema"
        ):
            full_schema = schema.model_json_schema()

        elif hasattr(
            schema,
            "schema"
        ):
            full_schema = schema.schema()

        else:
            return {}

        properties = full_schema.get(
            "properties",
            {}
        )

        required = set(
            full_schema.get(
                "required",
                []
            )
        )

        lean = {}

        for field_name, field_info in properties.items():

            field_type = field_info.get(
                "type",
                "any"
            )

            description = field_info.get(
                "description",
                ""
            )

            lean[field_name] = {
                "type": field_type,
                "required": field_name in required,
            }

            if description:

                lean[field_name]["description"] = (
                    description
                )

        return lean

    except Exception as e:

        print(
            f"\n⚠️ Could not build lean schema "
            f"for tool {getattr(tool, 'name', '?')}: {e}"
        )

        return {}


# =================================================
# WARMUP
# =================================================
#
# Call this once at FastAPI startup so the model is
# already loaded in memory before the first real user
# request arrives. For OpenAI this is essentially a
# no-op cost-wise (a single tiny request), but it
# still verifies your API key/connection works before
# users hit errors.
#
# =================================================

async def warmup_llm():

    try:

        print(
            f"\n🔥 Warming up {LLM_PROVIDER} model "
            f"(plain generation)..."
        )

        await llm.ainvoke(
            [
                HumanMessage(
                    content="hi"
                )
            ]
        )

        print(
            "✅ Plain generation warmed up."
        )

    except Exception as e:

        print(
            f"⚠️ Plain warmup failed (non-fatal): {e}"
        )

    # =============================================
    # WARM UP STRUCTURED / JSON MODE SEPARATELY
    # =============================================
    #
    # Ollama treats plain generation and
    # json-schema/tool-constrained generation as
    # DIFFERENT execution paths. Warming up plain
    # chat does NOT warm up structured output — the
    # first structured call still reports
    # done_reason='load' with empty content, exactly
    # like a cold start, even though the base model
    # weights are already resident in memory.
    #
    # So we run one throwaway structured call here,
    # using the exact same method (json_schema for
    # Ollama) that real agents will use, so THIS
    # path is also pre-loaded before any real
    # request arrives.
    #
    # For OpenAI this is a trivial extra request and
    # doubles as a sanity check that structured
    # output works with the current API key/model.
    # =============================================

    try:

        print(
            f"🔥 Warming up {LLM_PROVIDER} model "
            f"(structured output mode)..."
        )

        from pydantic import BaseModel

        class _WarmupSchema(BaseModel):
            ok: bool

        warmup_structured_llm = get_structured_llm(
            llm,
            _WarmupSchema,
        )

        # -----------------------------------------------
        # Use a padded prompt roughly proportional to a
        # real supervisor call (large tool catalog +
        # instructions), so this warmup actually exercises
        # the same code path that was failing — not just a
        # trivial one-liner that always succeeds.
        # -----------------------------------------------

        padding = (
            "This is warmup padding text used only to "
            "approximate the size of a real prompt. " * 200
        )

        await asyncio.wait_for(
            warmup_structured_llm.ainvoke(
                [
                    HumanMessage(
                        content=(
                            padding +
                            "\n\nReturn ok=true as JSON."
                        )
                    )
                ]
            ),
            timeout=90,
        )

        print(
            "✅ Structured output mode warmed up."
        )

    except Exception as e:

        print(
            f"⚠️ Structured warmup failed "
            f"(non-fatal, first real request may "
            f"be slower or need a retry): {e}"
        )

    print(
        "✅ Model warmup complete."
    )