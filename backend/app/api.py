import uuid
import traceback
import json

from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
)

from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import HumanMessage

from langgraph.types import Command


# ============================================================
# APPLICATION IMPORTS
# ============================================================

from app.agent import (
    llm,
    warmup_llm,
)

from app.graph import (
    create_graph,
)

from app.memory import (
    create_memory,
)

from app.memory_store import (
    initialize_memory,
)

from app.tools import (
    load_tools,
)


# ============================================================
# RAG IMPORTS
# ============================================================

from app.rag.loader import (
    load_file,
)

from app.rag.vector_store import (
    add_documents_to_store,
)

from app.rag.tools import (
    set_current_thread_id,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Office Assistant API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

graph = None

tools = None

llm_with_tools = None

memory_context = None


# ============================================================
# DIRECTORIES
# ============================================================

UPLOAD_DIR = Path(
    "data/uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ============================================================
# PENDING UPLOAD DIRECTORY
# ============================================================

PENDING_UPLOAD_DIR = Path(
    "data/pending_uploads"
)

PENDING_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {

    # Documents
    ".pdf",
    ".txt",
    ".docx",

    # Images
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".webp",

}


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):

    message: str

    thread_id: str | None = None


class ApprovalRequest(BaseModel):

    thread_id: str

    approved: bool

class UploadConfirmationRequest(BaseModel):

    pending_upload_id: str

    thread_id: str

    save_permanently: bool


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    global graph
    global tools
    global llm_with_tools
    global memory_context

    print("\n")
    print(
        "=========================================="
    )
    print(
        "🚀 OFFICE ASSISTANT STARTING"
    )
    print(
        "=========================================="
    )

    # ========================================================
    # INITIALIZE LONG-TERM MEMORY
    # ========================================================

    print("\n💾 Initializing long-term memory...")

    try:

        initialize_memory()

        print(
            "✅ Long-term memory initialized"
        )

    except Exception as e:

        print(
            "❌ Failed to initialize long-term memory"
        )

        print(
            "Error:",
            repr(e),
        )

        raise

    # ========================================================
    # WARM UP LLM
    # ========================================================

    print("\n🤖 Warming up LLM...")

    try:

        await warmup_llm()

        print(
            "✅ LLM ready"
        )

    except Exception as e:

        print(
            "❌ LLM warmup failed"
        )

        print(
            "Error:",
            repr(e),
        )

        raise


    # ========================================================
    # LOAD TOOLS
    # ========================================================

    print("\n🔧 Loading tools...")

    try:

        tools = await load_tools()

        print(
            f"✅ Loaded {len(tools)} tools."
        )

        for tool in tools:

            print(
                f"   • {tool.name}"
            )

    except Exception as e:

        print(
            "❌ Failed to load tools"
        )

        print(
            "Error:",
            repr(e),
        )

        raise


    # ========================================================
    # BIND TOOLS TO LLM
    # ========================================================

    print(
        "\n🔗 Binding tools to LLM..."
    )

    try:

        llm_with_tools = llm.bind_tools(
            tools
        )

        print(
            "✅ Tools bound to LLM"
        )

    except Exception as e:

        print(
            "❌ Failed to bind tools"
        )

        print(
            "Error:",
            repr(e),
        )

        raise


    # ========================================================
    # CREATE MEMORY
    # ========================================================

    print(
        "\n🧠 Creating memory..."
    )

    try:

        memory_context = create_memory()

        memory = (
            await memory_context.__aenter__()
        )

        print(
            "✅ Memory initialized"
        )

    except Exception as e:

        print(
            "❌ Failed to initialize memory"
        )

        print(
            "Error:",
            repr(e),
        )

        raise


    # ========================================================
    # CREATE LANGGRAPH
    # ========================================================

    print(
        "\n🕸️ Creating LangGraph..."
    )

    try:

        graph = create_graph(

            tools=tools,

            memory=memory,

        )

        print(
            "✅ LangGraph initialized"
        )

    except Exception as e:

        print(
            "❌ Failed to create LangGraph"
        )

        print(
            "Error:",
            repr(e),
        )

        raise


    # ========================================================
    # STARTUP COMPLETE
    # ========================================================

    print("\n")

    print(
        "=========================================="
    )

    print(
        "✅ OFFICE ASSISTANT READY"
    )

    print(
        "=========================================="
    )

    print("\n")


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
async def shutdown():

    global memory_context

    print("\n")

    print(
        "=========================================="
    )

    print(
        "🛑 SHUTTING DOWN"
    )

    print(
        "=========================================="
    )


    if memory_context:

        try:

            await memory_context.__aexit__(
                None,
                None,
                None,
            )

            print(
                "✅ Memory connection closed."
            )

        except Exception as e:

            print(
                "⚠️ Error closing memory:",
                repr(e),
            )


    print(
        "Shutdown complete."
    )


# ============================================================
# BUILD GRAPH CONFIG
# ============================================================

def build_config(
    thread_id: str,
):

    return {

        "configurable": {

            "thread_id":
                thread_id,

            "llm":
                llm,

            "llm_with_tools":
                llm_with_tools,

            "tools":
                tools,

        }

    }


# ============================================================
# APPROVAL DISPLAY BUILDER
# ============================================================

def build_approval_response(
    approval,
    thread_id,
):

    if not approval:

        return None


    tool = approval.get(
        "tool",
        "",
    )


    arguments = approval.get(
        "arguments",
        {},
    )


    risk = approval.get(
        "risk",
        "HIGH",
    )


    # ========================================================
    # DEFAULT APPROVAL
    # ========================================================

    approval_data = {

        "risk":
            risk,

        "title":
            "Confirmation Required",

        "message": (
            "The assistant is ready to perform "
            "an action that requires your confirmation."
        ),

        "reason": (
            "This operation may modify data, "
            "communicate externally, or have "
            "another significant effect."
        ),

        "warning": (
            "Please review this action before continuing."
        ),

    }


    # ========================================================
    # EMAIL APPROVAL
    # ========================================================

    if tool == "send_a_email":

        recipient = arguments.get(
            "to",
            "Unknown recipient",
        )

        subject = arguments.get(
            "subject",
            "No subject",
        )

        body = arguments.get(
            "body",
            "",
        )


        # ----------------------------------------------------
        # Hide internal FROM_TASK references
        # ----------------------------------------------------

        if (

            isinstance(
                body,
                str,
            )

            and body.startswith(
                "{FROM_TASK:"
            )

        ):

            body = (
                "Employee information retrieved "
                "from the previous step."
            )


        approval_data = {

            "risk":
                "HIGH",

            "title":
                "Send Employee Information",

            "message": (
                "The assistant is ready to send "
                "employee information by email."
            ),

            "reason": (
                "Sending an email communicates "
                "information outside the system."
            ),

            "recipient":
                recipient,

            "subject":
                subject,

            "information":
                body,

            "warning": (
                "This action will send information "
                "outside the system and cannot be "
                "automatically undone."
            ),

        }


    # ========================================================
    # DELETE OPERATION
    # ========================================================

    elif "delete" in tool.lower():

        approval_data = {

            "risk":
                risk,

            "title":
                "Delete Information",

            "message": (
                "The assistant is about to permanently "
                "delete information."
            ),

            "reason": (
                "Deleting information can be "
                "irreversible."
            ),

            "warning": (
                "Deleted information may not be "
                "recoverable."
            ),

        }


    # ========================================================
    # UPDATE / MODIFY OPERATION
    # ========================================================

    elif any(

        word in tool.lower()

        for word in [

            "update",
            "modify",
            "edit",
            "change",

        ]

    ):

        approval_data = {

            "risk":
                risk,

            "title":
                "Update Information",

            "message": (
                "The assistant is ready to modify "
                "information."
            ),

            "reason": (
                "This operation changes existing "
                "information."
            ),

            "warning": (
                "This action will change existing "
                "information."
            ),

        }


    # ========================================================
    # FINAL APPROVAL RESPONSE
    # ========================================================

    return {

        "status":
            "approval_required",

        "thread_id":
            thread_id,

        "approval":
            approval_data,

    }


# ============================================================
# GET PENDING APPROVAL
# ============================================================

async def get_pending_approval(
    config,
):

    try:

        state = await graph.aget_state(
            config
        )


        if state.tasks:

            for task in state.tasks:

                if task.interrupts:

                    return (
                        task.interrupts[0].value
                    )


    except Exception as e:

        print(
            "⚠️ Could not check approval:",
            repr(e),
        )


    return None


# ============================================================
# RESET EXECUTION STATE
# ============================================================

async def reset_execution_state(
    config,
):

    await graph.aupdate_state(

        config,

        {

            "execution_plan":
                [],

            "task_results":
                {},

            "approved_tasks":
                [],

            "pending_approval":
                None,

            "completed_tasks":
                [],

            "execution_complete":
                False,

        },

    )


# ============================================================
# EXTRACT MESSAGE CONTENT
# ============================================================

def extract_message_content(
    message,
):

    if not message:

        return ""


    content = getattr(
        message,
        "content",
        "",
    )


    # --------------------------------------------------------
    # Normal string
    # --------------------------------------------------------

    if isinstance(
        content,
        str,
    ):

        return content


    # --------------------------------------------------------
    # Structured content
    # --------------------------------------------------------

    if isinstance(
        content,
        list,
    ):

        parts = []


        for item in content:

            if isinstance(
                item,
                dict,
            ):

                text = item.get(
                    "text"
                )


                if text:

                    parts.append(
                        text
                    )


            elif isinstance(
                item,
                str,
            ):

                parts.append(
                    item
                )


        return "\n".join(
            parts
        )


    return str(
        content
    )


# ============================================================
# CHAT API
# ============================================================

@app.post("/chat")
async def chat(
    request: ChatRequest,
):

    global graph
    global tools
    global llm_with_tools


    print("\n")

    print(
        "=========================================="
    )

    print(
        "💬 /chat REQUEST RECEIVED"
    )

    print(
        "=========================================="
    )


    print(
        "Message:",
        request.message,
    )


    # ========================================================
    # CHECK INITIALIZATION
    # ========================================================

    if graph is None:

        print(
            "❌ Graph is None"
        )

        return {

            "status":
                "error",

            "response":
                "LangGraph is not initialized.",

        }


    if tools is None:

        print(
            "❌ Tools are None"
        )

        return {

            "status":
                "error",

            "response":
                "Tools are not loaded.",

        }


    # ========================================================
    # CREATE / RESTORE THREAD
    # ========================================================

    thread_id = (

        request.thread_id

        or str(
            uuid.uuid4()
        )

    )


    # --------------------------------------------------------
    # IMPORTANT
    #
    # Tell the RAG tool which temporary Chroma collection
    # belongs to this conversation.
    # --------------------------------------------------------

    set_current_thread_id(
        thread_id
    )


    print(
        "🧵 Thread ID:",
        thread_id,
    )


    # ========================================================
    # CREATE CONFIG
    # ========================================================

    config = build_config(
        thread_id
    )


    print(
        "✅ Graph config created"
    )


    # ========================================================
    # RESET EXECUTION STATE
    # ========================================================

    print(
        "\n🔄 Resetting execution state..."
    )


    try:

        await reset_execution_state(
            config
        )


        print(
            "✅ Execution state reset"
        )


    except Exception as e:

        print(
            "\n❌ Failed to reset execution state"
        )

        print(
            "Error:",
            repr(e),
        )


        traceback.print_exc()


        return {

            "status":
                "error",

            "thread_id":
                thread_id,

            "response": (
                "Failed to reset execution state: "
                f"{e}"
            ),

        }


    # ========================================================
    # RUN LANGGRAPH
    # ========================================================

    print(
        "\n🚀 Starting LangGraph..."
    )


    try:

        result = await graph.ainvoke(

            {

                "messages": [

                    HumanMessage(
                        content=request.message
                    )

                ]

            },

            config=config,

        )


        print(
            "\n✅ LangGraph execution finished"
        )


    except Exception as e:

        print(
            "\n❌ LANGGRAPH ERROR"
        )

        print(
            "Error type:",
            type(e).__name__,
        )

        print(
            "Error:",
            repr(e),
        )


        traceback.print_exc()


        return {

            "status":
                "error",

            "thread_id":
                thread_id,

            "response": (
                "LangGraph execution failed: "
                f"{e}"
            ),

        }


    # ========================================================
    # READ RESPONSE
    # ========================================================

    messages = result.get(
        "messages",
        [],
    )


    print(
        "📨 Message count:",
        len(messages),
    )


    answer = ""


    if messages:

        last_message = messages[-1]

        answer = extract_message_content(
            last_message
        )


    print(
        "🤖 Response:",
        repr(answer),
    )


    # ========================================================
    # CHECK APPROVAL
    # ========================================================

    print(
        "\n🔎 Checking for approval..."
    )


    approval = await get_pending_approval(
        config
    )


    print(
        "Approval:",
        approval,
    )


    # ========================================================
    # APPROVAL REQUIRED
    # ========================================================

    if approval:

        print(
            "\n⏸️ APPROVAL REQUIRED"
        )


        approval_response = (
            build_approval_response(

                approval,

                thread_id,

            )
        )


        approval_response[
            "response"
        ] = answer


        return approval_response


    # ========================================================
    # NORMAL RESPONSE
    # ========================================================

    print(
        "\n✅ Returning normal response"
    )


    return {

        "status":
            "completed",

        "thread_id":
            thread_id,

        "response":
            answer,

    }


# ============================================================
# APPROVAL API
# ============================================================

@app.post("/approval")
async def approval(
    request: ApprovalRequest,
):

    global graph


    print("\n")

    print(
        "=========================================="
    )

    print(
        "👤 HUMAN APPROVAL RESPONSE"
    )

    print(
        "=========================================="
    )


    print(
        "Thread:",
        request.thread_id,
    )


    print(
        "Approved:",
        request.approved,
    )


    # ========================================================
    # CHECK GRAPH
    # ========================================================

    if graph is None:

        return {

            "status":
                "error",

            "response":
                "LangGraph is not initialized.",

        }


    # ========================================================
    # RESTORE RAG THREAD
    # ========================================================

    set_current_thread_id(
        request.thread_id
    )


    # ========================================================
    # CREATE CONFIG
    # ========================================================

    config = build_config(
        request.thread_id
    )


    # ========================================================
    # RESUME GRAPH
    # ========================================================

    try:

        if request.approved:

            print(
                "✅ Resuming with approval..."
            )


            result = await graph.ainvoke(

                Command(
                    resume="yes"
                ),

                config=config,

            )


        else:

            print(
                "❌ Resuming with rejection..."
            )


            result = await graph.ainvoke(

                Command(
                    resume="no"
                ),

                config=config,

            )


    except Exception as e:

        print(
            "\n❌ APPROVAL RESUME ERROR"
        )

        print(
            "Error type:",
            type(e).__name__,
        )

        print(
            "Error:",
            repr(e),
        )


        traceback.print_exc()


        return {

            "status":
                "error",

            "thread_id":
                request.thread_id,

            "response": (
                "Failed to process approval: "
                f"{e}"
            ),

        }


    # ========================================================
    # CHECK FOR ANOTHER APPROVAL
    # ========================================================

    approval_data = await get_pending_approval(
        config
    )


    if approval_data:

        print(
            "\n⏸️ ANOTHER APPROVAL REQUIRED"
        )


        return build_approval_response(

            approval_data,

            request.thread_id,

        )


    # ========================================================
    # GET FINAL RESPONSE
    # ========================================================

    messages = result.get(
        "messages",
        [],
    )


    response = ""


    if messages:

        last_message = messages[-1]

        response = extract_message_content(
            last_message
        )


    print(
        "\n✅ Approval processing complete"
    )


    print(
        "Final response:",
        repr(response),
    )


    return {

        "status":
            "completed",

        "thread_id":
            request.thread_id,

        "response":
            response,

    }


# ============================================================
# FILE UPLOAD / RAG PREPARATION
# ============================================================

@app.post("/upload")
async def upload_file(

    file: UploadFile = File(...),

    thread_id: str = Form(...),

):
    """
    Upload a document and prepare it for confirmation.

    IMPORTANT:

    This endpoint DOES NOT add anything to Chroma.

    It only:

        1. validates the file
        2. saves it temporarily
        3. extracts the content
        4. confirms that readable content exists
        5. returns a pending_upload_id

    The frontend must then ask the user whether the
    document should be saved permanently.

    The actual RAG ingestion happens in:

        POST /upload/confirm
    """

    temp_path = None

    try:

        print()
        print(
            "=========================================="
        )

        print(
            "📎 RAG FILE UPLOAD"
        )

        print(
            "=========================================="
        )

        print(
            "Filename:",
            file.filename,
        )

        print(
            "Content type:",
            file.content_type,
        )

        print(
            "Thread ID:",
            thread_id,
        )

        # ====================================================
        # VALIDATE THREAD
        # ====================================================

        if not thread_id:

            return {

                "status":
                    "error",

                "response":
                    "Thread ID is required.",

            }

        # ====================================================
        # VALIDATE FILE NAME
        # ====================================================

        if not file.filename:

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "response":
                    "Filename is required.",

            }

        # ====================================================
        # VALIDATE EXTENSION
        # ====================================================

        original_path = Path(
            file.filename
        )

        extension = (
            original_path.suffix.lower()
        )

        if extension not in ALLOWED_EXTENSIONS:

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "response": (
                    f"Unsupported file type: "
                    f"{extension}"
                ),

            }

        # ====================================================
        # SAFE FILE NAME
        # ====================================================

        safe_filename = (
            original_path.name
        )

        # ====================================================
        # CREATE PENDING UPLOAD ID
        # ====================================================

        pending_upload_id = str(
            uuid.uuid4()
        )

        # ====================================================
        # CREATE TEMPORARY PATH
        # ====================================================

        temp_path = (

            PENDING_UPLOAD_DIR

            / (
                f"{pending_upload_id}"
                f"_{safe_filename}"
            )

        )

        # ====================================================
        # READ FILE
        # ====================================================

        contents = await file.read()

        if not contents:

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "response":
                    "Uploaded file is empty.",

            }

        # ====================================================
        # SAVE PENDING FILE
        # ====================================================

        with open(

            temp_path,

            "wb",

        ) as output_file:

            output_file.write(
                contents
            )

        print(
            "💾 Pending file saved:",
            temp_path,
        )

        print(
            "📦 File size:",
            len(contents),
            "bytes",
        )

        # ====================================================
        # TEST FILE EXTRACTION
        # ====================================================

        print(
            "\n📖 Checking document content..."
        )

        documents = load_file(
            temp_path
        )

        if not documents:

            # ------------------------------------------------
            # Remove invalid pending file
            # ------------------------------------------------

            try:

                if temp_path.exists():

                    temp_path.unlink()

            except Exception:

                pass

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "filename":
                    file.filename,

                "response": (
                    "No readable content was "
                    "found in the uploaded file."
                ),

            }

        print(
            "✅ Document content is readable."
        )

        print(
            "📄 Extracted sections:",
            len(documents),
        )

        # ====================================================
        # CREATE PENDING METADATA
        # ====================================================

        metadata_path = (

            PENDING_UPLOAD_DIR

            / f"{pending_upload_id}.json"

        )

        pending_metadata = {

            "pending_upload_id":
                pending_upload_id,

            "thread_id":
                thread_id,

            "filename":
                file.filename,

            "content_type":
                file.content_type,

            "size":
                len(contents),

            "file_path":
                str(temp_path),

        }

        with open(

            metadata_path,

            "w",

            encoding="utf-8",

        ) as metadata_file:

            json.dump(

                pending_metadata,

                metadata_file,

                indent=2,

            )

        print(
            "📝 Pending metadata saved:",
            metadata_path,
        )

        # ====================================================
        # IMPORTANT
        # ====================================================

        print()
        print(
            "⏸️ Waiting for user confirmation."
        )

        print(
            "The file has NOT been added to Chroma yet."
        )

        # ====================================================
        # RETURN CONFIRMATION REQUEST
        # ====================================================

        return {

            "status":
                "confirmation_required",

            "pending_upload_id":
                pending_upload_id,

            "thread_id":
                thread_id,

            "filename":
                file.filename,

            "content_type":
                file.content_type,

            "size":
                len(contents),

            "documents":
                len(documents),

            "response": (
                "File uploaded successfully. "
                "Do you want to save this document "
                "permanently for future conversations?"
            ),

            "options": {

                "save_permanently": (
                    "Save Permanently"
                ),

                "temporary": (
                    "Use Only This Chat"
                ),

            },

        }

    except Exception as e:

        print()
        print(
            "❌ FILE UPLOAD ERROR"
        )

        print(
            "Error type:",
            type(e).__name__,
        )

        print(
            "Error:",
            repr(e),
        )

        traceback.print_exc()

        # ====================================================
        # CLEANUP
        # ====================================================

        if temp_path:

            try:

                if temp_path.exists():

                    temp_path.unlink()

            except Exception:

                pass

        return {

            "status":
                "error",

            "thread_id":
                thread_id,

            "response": (
                "File upload failed: "
                f"{e}"
            ),

        }

# ============================================================
# CONFIRM RAG FILE STORAGE
# ============================================================

@app.post("/upload/confirm")
async def confirm_upload(
    request: UploadConfirmationRequest,
):
    """
    Finalize a pending upload.

    save_permanently=True
        → document becomes globally available.

    save_permanently=False
        → document remains available only to
          the current thread.

    Both choices ingest the document into Chroma.

    The difference is metadata scope.
    """

    pending_upload_id = (
        request.pending_upload_id
    )

    thread_id = (
        request.thread_id
    )

    save_permanently = (
        request.save_permanently
    )

    print()
    print(
        "=========================================="
    )

    print(
        "💾 RAG UPLOAD CONFIRMATION"
    )

    print(
        "=========================================="
    )

    print(
        "Pending upload:",
        pending_upload_id,
    )

    print(
        "Thread:",
        thread_id,
    )

    print(
        "Save permanently:",
        save_permanently,
    )

    metadata_path = (

        PENDING_UPLOAD_DIR

        / f"{pending_upload_id}.json"

    )

    # ========================================================
    # CHECK PENDING UPLOAD
    # ========================================================

    if not metadata_path.exists():

        return {

            "status":
                "error",

            "thread_id":
                thread_id,

            "response": (
                "Pending upload was not found "
                "or has already been processed."
            ),

        }

    temp_path = None

    try:

        # ====================================================
        # READ METADATA
        # ====================================================

        with open(

            metadata_path,

            "r",

            encoding="utf-8",

        ) as metadata_file:

            pending_metadata = json.load(
                metadata_file
            )

        stored_thread_id = (
            pending_metadata.get(
                "thread_id"
            )
        )

        filename = (
            pending_metadata.get(
                "filename"
            )
        )

        temp_path_string = (
            pending_metadata.get(
                "file_path"
            )
        )

        temp_path = Path(
            temp_path_string
        )

        # ====================================================
        # SECURITY CHECK
        # ====================================================

        if stored_thread_id != thread_id:

            print(
                "❌ Thread mismatch."
            )

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "response": (
                    "This upload does not belong "
                    "to the current conversation."
                ),

            }

        # ====================================================
        # CHECK FILE
        # ====================================================

        if not temp_path.exists():

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "response":
                    "Pending uploaded file no longer exists.",

            }

        # ====================================================
        # LOAD FILE AGAIN
        # ====================================================

        print(
            "\n📖 Loading pending document..."
        )

        documents = load_file(
            temp_path
        )

        if not documents:

            return {

                "status":
                    "error",

                "thread_id":
                    thread_id,

                "response": (
                    "Could not read the pending "
                    "document."
                ),

            }

        print(
            "✅ Document loaded."
        )

        print(
            "📄 Documents:",
            len(documents),
        )

        # ====================================================
        # INGEST INTO RAG
        # ====================================================

        if save_permanently:

            print()
            print(
                "📚 User selected:"
            )

            print(
                "   SAVE PERMANENTLY"
            )

            chunk_count = (
                add_documents_to_store(

                    documents=documents,

                    thread_id=None,

                    permanent=True,

                )
            )

            storage_message = (
                "The document has been permanently "
                "saved to the knowledge base and "
                "will be available in future conversations."
            )

        else:

            print()
            print(
                "🕐 User selected:"
            )

            print(
                "   USE ONLY THIS CHAT"
            )

            chunk_count = (
                add_documents_to_store(

                    documents=documents,

                    thread_id=thread_id,

                    permanent=False,

                )
            )

            storage_message = (
                "The document is available for this "
                "conversation only. It will not be "
                "available to other conversations."
            )

        # ====================================================
        # REMOVE PENDING FILE
        # ====================================================

        try:

            if temp_path.exists():

                temp_path.unlink()

                print(
                    "🗑️ Pending file removed."
                )

        except Exception as cleanup_error:

            print(
                "⚠️ Could not remove pending file:",
                repr(cleanup_error),
            )

        # ====================================================
        # REMOVE PENDING METADATA
        # ====================================================

        try:

            if metadata_path.exists():

                metadata_path.unlink()

                print(
                    "🗑️ Pending metadata removed."
                )

        except Exception as cleanup_error:

            print(
                "⚠️ Could not remove metadata:",
                repr(cleanup_error),
            )

        # ====================================================
        # SUCCESS
        # ====================================================

        print()
        print(
            "=========================================="
        )

        print(
            "✅ RAG UPLOAD CONFIRMATION COMPLETE"
        )

        print(
            "=========================================="
        )

        print(
            "Filename:",
            filename,
        )

        print(
            "Chunks:",
            chunk_count,
        )

        print(
            "Permanent:",
            save_permanently,
        )

        return {

            "status":
                "completed",

            "thread_id":
                thread_id,

            "pending_upload_id":
                pending_upload_id,

            "filename":
                filename,

            "chunks":
                chunk_count,

            "permanent":
                save_permanently,

            "response":
                storage_message,

        }

    except Exception as e:

        print()
        print(
            "❌ RAG CONFIRMATION ERROR"
        )

        print(
            "Error type:",
            type(e).__name__,
        )

        print(
            "Error:",
            repr(e),
        )

        traceback.print_exc()

        return {

            "status":
                "error",

            "thread_id":
                thread_id,

            "response": (
                "Failed to save the document: "
                f"{e}"
            ),

        }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
async def root():

    return {

        "status":
            "online",

        "message":
            "Office Assistant API is running",

        "service":
            "FastAPI + LangGraph + MCP",

    }


# ============================================================
# RAG HEALTH CHECK
# ============================================================

@app.get("/rag/health")
async def rag_health():

    return {

        "status":
            "ready",

        "embedding_provider":
            "configured in app.agent",

        "vector_database":
            "Chroma",

        "upload_directory":
            str(UPLOAD_DIR),

        "supported_extensions":
            sorted(
                ALLOWED_EXTENSIONS
            ),

    }