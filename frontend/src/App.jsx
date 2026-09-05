import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "./App.css";

const STORAGE_KEY = "office_assistant_chat_history";
const THEME_KEY = "office_assistant_theme";
const PINNED_KEY = "office_assistant_pinned";

function App() {
  // ==================================================
  // CURRENT CHAT
  // ==================================================

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState(null);
  const [approval, setApproval] = useState(null);

  // ==================================================
  // DOCUMENT UPLOAD CONFIRMATION
  // ==================================================

  const [pendingUploads, setPendingUploads] = useState([]);

  // ==================================================
  // CHAT HISTORY
  // ==================================================

  const [chatHistory, setChatHistory] = useState([]);

  // ==================================================
  // SIDEBAR
  // ==================================================

  const [sidebarOpen, setSidebarOpen] = useState(true);

  // ==================================================
  // THREE DOT MENU
  // ==================================================

  const [openMenuId, setOpenMenuId] = useState(null);

  // ==================================================
  // DELETE CONFIRMATION
  // ==================================================

  const [deleteChatId, setDeleteChatId] = useState(null);

  // ==================================================
  // THEME
  // ==================================================

  const [theme, setTheme] = useState("light");

  // ==================================================
  // SETTINGS
  // ==================================================

  const [settingsOpen, setSettingsOpen] = useState(false);

  // ==================================================
  // SEARCH
  // ==================================================

  const [searchQuery, setSearchQuery] = useState("");

  // ==================================================
  // PINNED CHATS
  // ==================================================

  const [pinnedChats, setPinnedChats] = useState([]);

  // ==================================================
  // COPY MESSAGE
  // ==================================================

  const [copiedMessageId, setCopiedMessageId] = useState(null);

  // ==================================================
  // REFS
  // ==================================================

  const menuRef = useRef(null);
  const settingsRef = useRef(null);
  const fileInputRef = useRef(null);

  // ==================================================
  // FILE UPLOAD
  // ==================================================

  const [selectedFiles, setSelectedFiles] = useState([]);

  // ==================================================
  // LOAD THEME
  // ==================================================

  useEffect(() => {
    try {
      const savedTheme = localStorage.getItem(THEME_KEY);

      if (savedTheme) {
        setTheme(savedTheme);

        document.documentElement.setAttribute(
          "data-theme",
          savedTheme
        );
      } else {
        document.documentElement.setAttribute(
          "data-theme",
          "light"
        );
      }
    } catch (error) {
      console.error("Failed to load theme:", error);
    }
  }, []);

  // ==================================================
  // SAVE THEME
  // ==================================================

  useEffect(() => {
    try {
      localStorage.setItem(THEME_KEY, theme);

      document.documentElement.setAttribute(
        "data-theme",
        theme
      );
    } catch (error) {
      console.error("Failed to save theme:", error);
    }
  }, [theme]);

  // ==================================================
  // LOAD PINNED CHATS
  // ==================================================

  useEffect(() => {
    try {
      const savedPinned = localStorage.getItem(PINNED_KEY);

      if (savedPinned) {
        const parsed = JSON.parse(savedPinned);

        if (Array.isArray(parsed)) {
          setPinnedChats(parsed);
        }
      }
    } catch (error) {
      console.error(
        "Failed to load pinned chats:",
        error
      );
    }
  }, []);

  // ==================================================
  // SAVE PINNED CHATS
  // ==================================================

  useEffect(() => {
    try {
      localStorage.setItem(
        PINNED_KEY,
        JSON.stringify(pinnedChats)
      );
    } catch (error) {
      console.error(
        "Failed to save pinned chats:",
        error
      );
    }
  }, [pinnedChats]);

  // ==================================================
  // LOAD CHAT HISTORY
  // ==================================================

  useEffect(() => {
    try {
      const storedHistory =
        localStorage.getItem(STORAGE_KEY);

      if (storedHistory) {
        const parsedHistory =
          JSON.parse(storedHistory);

        if (Array.isArray(parsedHistory)) {
          setChatHistory(parsedHistory);
        }
      }
    } catch (error) {
      console.error(
        "Failed to load chat history:",
        error
      );
    }
  }, []);

  // ==================================================
  // SAVE CHAT HISTORY
  // ==================================================

  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chatHistory)
      );
    } catch (error) {
      console.error(
        "Failed to save chat history:",
        error
      );
    }
  }, [chatHistory]);

  // ==================================================
  // CLOSE MENUS
  // ==================================================

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setOpenMenuId(null);
      }

      if (
        settingsRef.current &&
        !settingsRef.current.contains(event.target)
      ) {
        setSettingsOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  // ==================================================
  // TOGGLE THEME
  // ==================================================

  const toggleTheme = () => {
    setTheme((previous) =>
      previous === "light" ? "dark" : "light"
    );
  };

  // ==================================================
  // PIN CHAT
  // ==================================================

  const togglePinChat = (chatId) => {
    setPinnedChats((previous) => {
      if (previous.includes(chatId)) {
        return previous.filter(
          (id) => id !== chatId
        );
      }

      return [...previous, chatId];
    });
  };

  // ==================================================
  // IS PINNED
  // ==================================================

  const isChatPinned = (chatId) => {
    return pinnedChats.includes(chatId);
  };

  // ==================================================
  // COPY MESSAGE
  // ==================================================

  const copyMessage = (
    content,
    messageIndex
  ) => {
    navigator.clipboard
      .writeText(content)
      .then(() => {
        setCopiedMessageId(messageIndex);

        setTimeout(() => {
          setCopiedMessageId(null);
        }, 2000);
      })
      .catch((error) => {
        console.error(
          "Failed to copy message:",
          error
        );
      });
  };

  // ==================================================
  // FORMAT TIME
  // ==================================================

  const formatTime = (timestamp) => {
    if (!timestamp) {
      return "";
    }

    return new Date(timestamp).toLocaleTimeString(
      undefined,
      {
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  };

  // ==================================================
  // FORMAT DATE
  // ==================================================

  const formatDate = (timestamp) => {
    if (!timestamp) {
      return "";
    }

    return new Date(timestamp).toLocaleDateString(
      undefined,
      {
        day: "2-digit",
        month: "short",
      }
    );
  };

  // ==================================================
  // SAVE CURRENT CHAT
  // ==================================================

  const saveCurrentChat = (
    currentMessages = messages,
    currentThreadId = threadId
  ) => {
    if (
      !currentMessages ||
      currentMessages.length === 0
    ) {
      return;
    }

    const id =
      currentThreadId ||
      `local-${Date.now()}`;

    const firstUserMessage =
      currentMessages.find(
        (item) => item.role === "user"
      );

    const title =
      firstUserMessage?.content?.slice(
        0,
        45
      ) || "New Chat";

    const updatedChat = {
      id,
      threadId: currentThreadId,
      title,
      messages: currentMessages,
      updatedAt: Date.now(),
    };

    setChatHistory((previous) => {
      const existingIndex =
        previous.findIndex(
          (chat) => chat.id === id
        );

      if (existingIndex !== -1) {
        const updated = [...previous];

        updated[existingIndex] = updatedChat;

        return updated.sort(
          (a, b) =>
            b.updatedAt - a.updatedAt
        );
      }

      return [
        updatedChat,
        ...previous,
      ];
    });
  };

  // ==================================================
  // OPEN FILE PICKER
  // ==================================================

  const openFilePicker = () => {
    if (
      loading ||
      approval ||
      pendingUploads.length > 0
    ) {
      return;
    }

    fileInputRef.current?.click();
  };

  // ==================================================
  // FILE SELECT
  // ==================================================

  const handleFileSelect = (event) => {
    const files = Array.from(
      event.target.files || []
    );

    if (!files.length) {
      return;
    }

    setSelectedFiles((previous) => {
      const existing = new Set(
        previous.map(
          (file) =>
            `${file.name}-${file.size}-${file.lastModified}`
        )
      );

      const newFiles = files.filter(
        (file) =>
          !existing.has(
            `${file.name}-${file.size}-${file.lastModified}`
          )
      );

      return [
        ...previous,
        ...newFiles,
      ];
    });

    event.target.value = "";
  };

  // ==================================================
  // REMOVE FILE
  // ==================================================

  const removeSelectedFile = (
    fileToRemove
  ) => {
    setSelectedFiles((previous) =>
      previous.filter(
        (file) =>
          !(
            file.name ===
              fileToRemove.name &&
            file.size ===
              fileToRemove.size &&
            file.lastModified ===
              fileToRemove.lastModified
          )
      )
    );
  };

  // ==================================================
  // CAN SEND
  // ==================================================

  const canSend =
    !loading &&
    !approval &&
    pendingUploads.length === 0 &&
    (
      message.trim().length > 0 ||
      selectedFiles.length > 0
    );

  // ==================================================
  // UPLOAD SELECTED FILES
  // ==================================================

  const uploadSelectedFiles = async (
    currentThreadId,
    currentMessage
  ) => {
    const uploadResults = [];

    for (const file of selectedFiles) {
      const formData = new FormData();

      formData.append("file", file);
      formData.append(
        "thread_id",
        currentThreadId
      );

      console.log(
        "================================"
      );

      console.log(
        "Uploading file to /upload"
      );

      console.log(
        "File:",
        file.name
      );

      console.log(
        "Thread ID:",
        currentThreadId
      );

      console.log(
        "================================"
      );

      const response = await fetch(
        "http://localhost:8080/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        let errorText =
          `HTTP error: ${response.status}`;

        try {
          const errorData =
            await response.json();

          errorText =
            errorData.detail
              ? JSON.stringify(
                  errorData.detail
                )
              : JSON.stringify(
                  errorData
                );
        } catch {
          // Ignore JSON parsing failure.
        }

        throw new Error(
          `Failed to upload ${file.name}: ${errorText}`
        );
      }

      const data =
        await response.json();

      console.log(
        "Upload response:",
        data
      );

      if (
        data.status ===
        "error"
      ) {
        throw new Error(
          `Failed to process ${file.name}: ${
            data.response ||
            data.message ||
            "Unknown error"
          }`
        );
      }

      uploadResults.push({
        ...data,

        file_name:
          data.file_name ||
          data.filename ||
          file.name,

        message:
          currentMessage ||
          "Please analyze the uploaded file.",
      });
    }

    return uploadResults;
  };

  // ==================================================
  // SEND CHAT REQUEST
  // ==================================================

  const sendChatRequest = async (
    currentThreadId,
    userMessage,
    currentMessages
  ) => {
    const requestBody = {
      message: userMessage,
      thread_id: currentThreadId,
    };

    console.log(
      "================================"
    );

    console.log(
      "Sending JSON /chat request"
    );

    console.log(
      "Message:",
      userMessage
    );

    console.log(
      "Thread ID:",
      currentThreadId
    );

    console.log(
      "================================"
    );

    const response = await fetch(
      "http://localhost:8080/chat",
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          Accept:
            "application/json",
        },

        body: JSON.stringify(
          requestBody
        ),
      }
    );

    if (!response.ok) {
      let errorText =
        `HTTP error: ${response.status}`;

      try {
        const errorData =
          await response.json();

        errorText =
          errorData.detail
            ? JSON.stringify(
                errorData.detail
              )
            : JSON.stringify(
                errorData
              );
      } catch {
        // Ignore JSON parsing failure.
      }

      throw new Error(
        errorText
      );
    }

    const data =
      await response.json();

    console.log(
      "Backend /chat response:",
      data
    );

    const responseThreadId =
      data.thread_id ||
      currentThreadId;

    if (data.thread_id) {
      setThreadId(
        data.thread_id
      );
    }

    // ==================================================
    // APPROVAL REQUIRED
    // ==================================================

    if (
      data.status ===
      "approval_required"
    ) {
      setApproval(
        data.approval
      );

      saveCurrentChat(
        currentMessages,
        responseThreadId
      );

      return data;
    }

    // ==================================================
    // NORMAL RESPONSE
    // ==================================================

    if (data.response) {
      const finalMessages = [
        ...currentMessages,
        {
          role: "assistant",
          content:
            data.response,
          timestamp: Date.now(),
        },
      ];

      setMessages(
        finalMessages
      );

      saveCurrentChat(
        finalMessages,
        responseThreadId
      );
    } else {
      saveCurrentChat(
        currentMessages,
        responseThreadId
      );
    }

    return data;
  };

  // ==================================================
  // SEND MESSAGE
  // ==================================================

  const sendMessage = async () => {
    if (!canSend) {
      return;
    }

    const typedMessage =
      message.trim();

    const hasFiles =
      selectedFiles.length > 0;

    const uploadedFileNames =
      selectedFiles.map(
        (file) => file.name
      );

    const displayMessage =
      typedMessage ||
      (
        hasFiles
          ? `📎 ${uploadedFileNames.join(", ")}`
          : ""
      );

    const updatedMessages = [
      ...messages,
      {
        role: "user",
        content: displayMessage,
        timestamp: Date.now(),
      },
    ];

    setMessages(
      updatedMessages
    );

    setMessage("");
    setLoading(true);

    const currentThreadId =
      threadId ||
      crypto.randomUUID();

    if (!threadId) {
      setThreadId(
        currentThreadId
      );
    }

    try {
      // ==================================================
      // FILE FLOW
      // ==================================================

      if (hasFiles) {
        console.log(
          "================================"
        );

        console.log(
          `Uploading ${selectedFiles.length} file(s) before chat...`
        );

        console.log(
          "================================"
        );

        const userMessage =
          typedMessage ||
          "Please analyze the uploaded file.";

        const uploadResults =
          await uploadSelectedFiles(
            currentThreadId,
            userMessage
          );

        console.log(
          "All upload results:",
          uploadResults
        );

        const confirmationRequired =
          uploadResults.filter(
            (upload) =>
              upload.status ===
              "confirmation_required"
          );

        if (
          confirmationRequired.length >
          0
        ) {
          console.log(
            "================================"
          );

          console.log(
            "Document confirmation required."
          );

          console.log(
            "Pending uploads:",
            confirmationRequired
          );

          console.log(
            "================================"
          );

          const pendingItems =
            confirmationRequired.map(
              (upload) => ({
                pending_upload_id:
                  upload.pending_upload_id,

                file_name:
                  upload.file_name ||
                  upload.filename ||
                  "Uploaded document",

                message:
                  upload.message ||
                  userMessage,
              })
            );

          const invalidUpload =
            pendingItems.find(
              (item) =>
                !item.pending_upload_id
            );

          if (invalidUpload) {
            throw new Error(
              `Backend returned confirmation_required without pending_upload_id for ${invalidUpload.file_name}`
            );
          }

          setPendingUploads(
            pendingItems
          );

          setSelectedFiles([]);

          saveCurrentChat(
            updatedMessages,
            currentThreadId
          );

          return;
        }

        setSelectedFiles([]);

        await sendChatRequest(
          currentThreadId,
          userMessage,
          updatedMessages
        );

        return;
      }

      // ==================================================
      // NORMAL CHAT WITHOUT FILE
      // ==================================================

      const userMessage =
        typedMessage;

      await sendChatRequest(
        currentThreadId,
        userMessage,
        updatedMessages
      );
    } catch (error) {
      console.error(
        "Chat error:",
        error
      );

      const errorMessages = [
        ...updatedMessages,
        {
          role: "assistant",
          content:
            `Backend error: ${error.message}`,
          timestamp: Date.now(),
        },
      ];

      setMessages(
        errorMessages
      );

      saveCurrentChat(
        errorMessages,
        currentThreadId
      );
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // HANDLE DOCUMENT CONFIRMATION
  // ==================================================

  const handleUploadConfirmation = async (
    savePermanently
  ) => {
    if (
      pendingUploads.length === 0 ||
      !threadId ||
      loading
    ) {
      return;
    }

    setLoading(true);

    try {
      console.log(
        "================================"
      );

      console.log(
        "Confirming document upload(s)"
      );

      console.log(
        "Thread ID:",
        threadId
      );

      console.log(
        "Save Permanently:",
        savePermanently
      );

      console.log(
        "Pending Uploads:",
        pendingUploads
      );

      console.log(
        "================================"
      );

      for (
        const pendingUpload of pendingUploads
      ) {
        console.log(
          "Confirming:",
          pendingUpload.file_name
        );

        console.log(
          "Pending Upload ID:",
          pendingUpload.pending_upload_id
        );

        const response =
          await fetch(
            "http://localhost:8080/upload/confirm",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",

                Accept:
                  "application/json",
              },

              body: JSON.stringify({
                thread_id:
                  threadId,

                pending_upload_id:
                  pendingUpload.pending_upload_id,

                save_permanently:
                  savePermanently,
              }),
            }
          );

        if (!response.ok) {
          let errorText =
            `HTTP error: ${response.status}`;

          try {
            const errorData =
              await response.json();

            errorText =
              errorData.detail
                ? JSON.stringify(
                    errorData.detail
                  )
                : JSON.stringify(
                    errorData
                  );
          } catch {
            // Ignore JSON parsing failure.
          }

          throw new Error(
            `Failed to confirm ${pendingUpload.file_name}: ${errorText}`
          );
        }

        const data =
          await response.json();

        console.log(
          "Upload confirmation response:",
          data
        );

        if (
          data.status ===
          "error"
        ) {
          throw new Error(
            data.response ||
            data.message ||
            `Failed to confirm ${pendingUpload.file_name}`
          );
        }
      }

      console.log(
        "All document confirmations completed."
      );

      const userMessage =
        pendingUploads[0]?.message ||
        "Please analyze the uploaded file.";

      setPendingUploads([]);

      const currentMessages =
        messages;

      await sendChatRequest(
        threadId,
        userMessage,
        currentMessages
      );
    } catch (error) {
      console.error(
        "Document confirmation error:",
        error
      );

      const errorMessages = [
        ...messages,
        {
          role: "assistant",
          content:
            `Document confirmation error: ${error.message}`,
          timestamp: Date.now(),
        },
      ];

      setMessages(
        errorMessages
      );

      saveCurrentChat(
        errorMessages,
        threadId
      );
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // HANDLE APPROVAL
  // ==================================================

  const handleApproval = async (
    approved
  ) => {
    if (
      !threadId ||
      loading
    ) {
      return;
    }

    setLoading(true);

    try {
      const response =
        await fetch(
          "http://localhost:8080/approval",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Accept:
                "application/json",
            },

            body: JSON.stringify({
              thread_id:
                threadId,

              approved:
                approved,
            }),
          }
        );

      if (!response.ok) {
        let errorText =
          `HTTP error: ${response.status}`;

        try {
          const errorData =
            await response.json();

          errorText =
            errorData.detail
              ? JSON.stringify(
                  errorData.detail
                )
              : JSON.stringify(
                  errorData
                );
        } catch {
          // Ignore JSON parsing failure.
        }

        throw new Error(
          errorText
        );
      }

      const data =
        await response.json();

      console.log(
        "Approval response:",
        data
      );

      if (
        data.status ===
        "approval_required"
      ) {
        setApproval(
          data.approval
        );

        return;
      }

      setApproval(null);

      if (data.response) {
        const finalMessages = [
          ...messages,
          {
            role: "assistant",
            content:
              data.response,
            timestamp: Date.now(),
          },
        ];

        setMessages(
          finalMessages
        );

        saveCurrentChat(
          finalMessages,
          threadId
        );
      }
    } catch (error) {
      console.error(
        "Approval error:",
        error
      );

      const errorMessages = [
        ...messages,
        {
          role: "assistant",
          content:
            `Approval error: ${error.message}`,
          timestamp: Date.now(),
        },
      ];

      setMessages(
        errorMessages
      );

      saveCurrentChat(
        errorMessages,
        threadId
      );

      setApproval(null);
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // NEW CHAT
  // ==================================================

  const startNewChat = () => {
    if (messages.length > 0) {
      saveCurrentChat(
        messages,
        threadId
      );
    }

    setMessages([]);
    setMessage("");
    setThreadId(null);
    setApproval(null);
    setPendingUploads([]);
    setLoading(false);
    setSelectedFiles([]);
    setOpenMenuId(null);
    setSearchQuery("");
  };

  // ==================================================
  // OPEN PREVIOUS CHAT
  // ==================================================

  const openChat = (chat) => {
    if (
      loading ||
      pendingUploads.length > 0
    ) {
      return;
    }

    setMessages(
      chat.messages || []
    );

    setThreadId(
      chat.threadId || null
    );

    setApproval(null);
    setPendingUploads([]);
    setMessage("");
    setSelectedFiles([]);
    setOpenMenuId(null);
    setSearchQuery("");
  };

  // ==================================================
  // CHAT MENU
  // ==================================================

  const toggleChatMenu = (
    event,
    chatId
  ) => {
    event.stopPropagation();

    setOpenMenuId(
      (previous) =>
        previous === chatId
          ? null
          : chatId
    );
  };

  // ==================================================
  // DELETE REQUEST
  // ==================================================

  const requestDeleteChat = (
    event,
    chatId
  ) => {
    event.stopPropagation();

    setOpenMenuId(null);
    setDeleteChatId(chatId);
  };

  // ==================================================
  // CANCEL DELETE
  // ==================================================

  const cancelDelete = () => {
    setDeleteChatId(null);
  };

  // ==================================================
  // CONFIRM DELETE
  // ==================================================

  const confirmDelete = () => {
    if (!deleteChatId) {
      return;
    }

    setChatHistory(
      (previous) =>
        previous.filter(
          (chat) =>
            chat.id !==
            deleteChatId
        )
    );

    setPinnedChats(
      (previous) =>
        previous.filter(
          (id) =>
            id !==
            deleteChatId
        )
    );

    const currentChatId =
      threadId;

    const chatToDelete =
      chatHistory.find(
        (chat) =>
          chat.id ===
          deleteChatId
      );

    if (
      chatToDelete &&
      chatToDelete.threadId ===
        currentChatId
    ) {
      setMessages([]);
      setThreadId(null);
      setApproval(null);
      setPendingUploads([]);
      setMessage("");
      setSelectedFiles([]);
    }

    setDeleteChatId(null);
  };

  // ==================================================
  // KEYBOARD
  // ==================================================

  const handleKeyDown = (
    event
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (canSend) {
        sendMessage();
      }
    }
  };

  // ==================================================
  // PINNED CHATS
  // ==================================================

  const getPinnedChats = () => {
    return chatHistory.filter(
      (chat) =>
        pinnedChats.includes(
          chat.id
        )
    );
  };

  // ==================================================
  // RECENT CHATS
  // ==================================================

  const getRecentChats = () => {
    const recent =
      chatHistory.filter(
        (chat) =>
          !pinnedChats.includes(
            chat.id
          )
      );

    if (!searchQuery.trim()) {
      return recent;
    }

    const query =
      searchQuery.toLowerCase();

    return recent.filter(
      (chat) =>
        chat.title
          .toLowerCase()
          .includes(query) ||
        formatDate(
          chat.updatedAt
        )
          .toLowerCase()
          .includes(query)
    );
  };

  // ==================================================
  // GROUP CHATS
  // ==================================================

  const groupChatsByDate = (
    chats
  ) => {
    const startOfToday =
      new Date();

    startOfToday.setHours(
      0,
      0,
      0,
      0
    );

    const startOfYesterday =
      new Date(
        startOfToday
      );

    startOfYesterday.setDate(
      startOfYesterday.getDate() - 1
    );

    const groups = {
      Today: [],
      Yesterday: [],
      Older: [],
    };

    for (const chat of chats) {
      const chatDate =
        new Date(
          chat.updatedAt || 0
        );

      if (
        chatDate >=
        startOfToday
      ) {
        groups.Today.push(chat);
      } else if (
        chatDate >=
        startOfYesterday
      ) {
        groups.Yesterday.push(
          chat
        );
      } else {
        groups.Older.push(chat);
      }
    }

    return groups;
  };

  // ==================================================
  // SUGGESTION CARDS
  // ==================================================

  const suggestionCards = [
    {
      icon: "📁",
      title: "List files",
      description:
        "See every file available in the workspace.",
      prompt:
        "List all files",
    },
    {
      icon: "🌤️",
      title: "Check weather",
      description:
        "Get a live forecast for any city you need.",
      prompt:
        "Get weather forecast for Valsad",
    },
    {
      icon: "👤",
      title: "Find employee",
      description:
        "Look up employee details by ID.",
      prompt:
        "Find employee 1",
    },
    {
      icon: "📄",
      title: "Company policy",
      description:
        "Ask about leave, HR, or office policies.",
      prompt:
        "What is the leave policy?",
    },
  ];

  // ==================================================
  // FILE PREVIEW
  // ==================================================

  const renderSelectedFiles = () => {
    if (selectedFiles.length === 0) {
      return null;
    }

    return (
      <div
        className="selected-files"
        style={{
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "8px",
          width: "100%",
          padding: "8px 12px 4px 12px",
          boxSizing: "border-box",
        }}
      >
        {selectedFiles.map(
          (file) => (
            <div
              className="selected-file"
              key={`${file.name}-${file.size}-${file.lastModified}`}
              style={{
                display: "inline-flex",
                alignItems: "center",
                width: "fit-content",
                maxWidth: "100%",
                gap: "6px",
                padding: "6px 8px",
                borderRadius: "8px",
                boxSizing: "border-box",
              }}
            >
              <span
                className="selected-file-icon"
                style={{
                  flexShrink: 0,
                }}
              >
                {file.type.startsWith(
                  "image/"
                )
                  ? "🖼️"
                  : "📄"}
              </span>

              <span
                className="selected-file-name"
                title={file.name}
                style={{
                  maxWidth: "280px",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {file.name}
              </span>

              <button
                type="button"
                className="selected-file-remove"
                onClick={() =>
                  removeSelectedFile(
                    file
                  )
                }
                style={{
                  flexShrink: 0,
                  marginLeft: "0",
                }}
              >
                ×
              </button>
            </div>
          )
        )}
      </div>
    );
  };

  // ==================================================
  // PORTAL CHAT MENU
  // ==================================================
  //
  // IMPORTANT:
  // The menu is rendered directly into document.body.
  //
  // This prevents the menu from being clipped by
  // the scrolling chat-history container.
  //
  // ==================================================

  const renderChatMenu = (chat) => {
    if (openMenuId !== chat.id) {
      return null;
    }

    const button = document.querySelector(
      `[data-chat-menu-id="${chat.id}"]`
    );

    if (!button) {
      return null;
    }

    const rect =
      button.getBoundingClientRect();

    return createPortal(
      <div
        ref={menuRef}
        className="chat-menu chat-menu-portal"
        style={{
          position: "fixed",
          top: `${rect.bottom + 4}px`,
          right: `${Math.max(
            8,
            window.innerWidth - rect.right
          )}px`,
          zIndex: 99999,
        }}
        onClick={(event) => {
          event.stopPropagation();
        }}
      >
        <button
          className="menu-pin"
          onClick={(event) => {
            event.stopPropagation();

            togglePinChat(
              chat.id
            );

            setOpenMenuId(null);
          }}
        >
          <span>
            {isChatPinned(chat.id)
              ? "📍"
              : "📌"}
          </span>

          <span>
            {isChatPinned(chat.id)
              ? "Unpin"
              : "Pin"}
          </span>
        </button>

        <button
          className="menu-delete"
          onClick={(event) =>
            requestDeleteChat(
              event,
              chat.id
            )
          }
        >
          <span>🗑️</span>

          <span>
            Delete
          </span>
        </button>
      </div>,
      document.body
    );
  };

  // ==================================================
  // RENDER
  // ==================================================

  return (
    <div
      className="app"
      data-theme={theme}
    >
      {/* ==================================================
          SHARED FILE INPUT
      ================================================== */}

      <input
        ref={fileInputRef}
        type="file"
        className="file-input-hidden"
        accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
        multiple
        onChange={handleFileSelect}
      />

      {/* ==================================================
          SIDEBAR
      ================================================== */}

      <aside
        className={`sidebar ${
          sidebarOpen
            ? "sidebar-open"
            : "sidebar-closed"
        }`}
      >
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="brand-icon">
              🏢
            </div>

            {sidebarOpen && (
              <div>
                <strong>
                  Office Assistant
                </strong>

                <span>
                  AI Workspace
                </span>
              </div>
            )}
          </div>

          <button
            className="sidebar-toggle"
            onClick={() =>
              setSidebarOpen(
                !sidebarOpen
              )
            }
          >
            {sidebarOpen
              ? "‹"
              : "›"}
          </button>
        </div>

        <button
          className="new-chat-button"
          onClick={
            startNewChat
          }
          disabled={loading}
        >
          <span className="new-chat-icon">
            ＋
          </span>

          {sidebarOpen && (
            <span>
              New Chat
            </span>
          )}
        </button>

        {sidebarOpen && (
          <div className="features-section">
            <div className="history-title">
              Features
            </div>

            <div className="feature-item feature-item-active">
              <span className="feature-icon">
                💬
              </span>

              <span>
                AI Chat
              </span>
            </div>
          </div>
        )}

        {sidebarOpen && (
          <div className="history-section">
            {/* ==================================================
                FIXED SEARCH
            ================================================== */}

            <div className="search-container">
              <input
                type="text"
                className="search-input"
                placeholder="🔍 Search chats..."
                value={
                  searchQuery
                }
                onChange={(e) =>
                  setSearchQuery(
                    e.target.value
                  )
                }
              />

              {searchQuery && (
                <button
                  className="search-clear"
                  onClick={() =>
                    setSearchQuery("")
                  }
                >
                  ✕
                </button>
              )}
            </div>

            {/* ==================================================
                FIXED PINNED SECTION
            ================================================== */}

            {getPinnedChats()
              .length > 0 && (
              <div className="pinned-section">
                <div className="history-title">
                  📌 Pinned
                </div>

                <div className="history-list">
                  {getPinnedChats().map(
                    (chat) => (
                      <div
                        key={
                          chat.id
                        }
                        className="history-item-wrapper"
                      >
                        <button
                          className="history-item"
                          onClick={() =>
                            openChat(
                              chat
                            )
                          }
                        >
                          <span className="history-icon">
                            📌
                          </span>

                          <span className="history-info">
                            <span className="history-name">
                              {
                                chat.title
                              }
                            </span>

                            <span className="history-date">
                              {formatDate(
                                chat.updatedAt
                              )}
                            </span>
                          </span>
                        </button>

                        <div className="chat-menu-container">
                          <button
                            className="chat-menu-button"
                            data-chat-menu-id={
                              chat.id
                            }
                            onClick={(
                              event
                            ) =>
                              toggleChatMenu(
                                event,
                                chat.id
                              )
                            }
                          >
                            ⋮
                          </button>

                          {renderChatMenu(
                            chat
                          )}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {/* ==================================================
                SCROLLING CHAT HISTORY ONLY
            ================================================== */}

            <div className="chat-history-scroll">
              {getRecentChats()
                .length === 0 &&
                searchQuery ===
                  "" && (
                  <div className="empty-history">
                    <div>
                      💬
                    </div>

                    <span>
                      No previous chats
                    </span>
                  </div>
                )}

              {getRecentChats()
                .length === 0 &&
                searchQuery !==
                  "" && (
                  <div className="empty-history">
                    <div>
                      🔍
                    </div>

                    <span>
                      No chats found
                    </span>
                  </div>
                )}

              {Object.entries(
                groupChatsByDate(
                  getRecentChats()
                )
              ).map(
                ([
                  groupLabel,
                  chats,
                ]) =>
                  chats.length >
                    0 && (
                    <div
                      key={
                        groupLabel
                      }
                    >
                      <div className="history-title">
                        {
                          groupLabel
                        }
                      </div>

                      <div className="history-list">
                        {chats.map(
                          (chat) => (
                            <div
                              key={
                                chat.id
                              }
                              className="history-item-wrapper"
                            >
                              <button
                                className="history-item"
                                onClick={() =>
                                  openChat(
                                    chat
                                  )
                                }
                              >
                                <span className="history-icon">
                                  💬
                                </span>

                                <span className="history-info">
                                  <span className="history-name">
                                    {
                                      chat.title
                                    }
                                  </span>
                                </span>
                              </button>

                              <div className="chat-menu-container">
                                <button
                                  className="chat-menu-button"
                                  data-chat-menu-id={
                                    chat.id
                                  }
                                  onClick={(
                                    event
                                  ) =>
                                    toggleChatMenu(
                                      event,
                                      chat.id
                                    )
                                  }
                                >
                                  ⋮
                                </button>

                                {renderChatMenu(
                                  chat
                                )}
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )
              )}
            </div>
          </div>
        )}

        {sidebarOpen && (
          <div className="sidebar-footer">
            <div className="status-dot"></div>

            <span>
              AI Assistant Online
            </span>
          </div>
        )}
      </aside>

      {/* ==================================================
          MAIN AREA
      ================================================== */}

      <div className="main-area">
        <header className="header">
          <div className="header-left">
            {!sidebarOpen && (
              <button
                className="mobile-menu-button"
                onClick={() =>
                  setSidebarOpen(
                    true
                  )
                }
              >
                ☰
              </button>
            )}

            <div>
              <h1>
                Office Assistant
              </h1>

              <p>
                LangGraph · MCP · FastAPI
              </p>
            </div>
          </div>

          <div className="header-right">
            <button
              className="theme-toggle"
              onClick={
                toggleTheme
              }
              title={
                theme ===
                "light"
                  ? "Dark Mode"
                  : "Light Mode"
              }
            >
              {theme ===
              "light"
                ? "🌙"
                : "☀️"}
            </button>

            <div
              className="settings-container"
              ref={
                settingsRef
              }
            >
              <button
                className="settings-button"
                onClick={() =>
                  setSettingsOpen(
                    !settingsOpen
                  )
                }
                title="Settings"
              >
                ⚙️
              </button>

              {settingsOpen && (
                <div className="settings-panel">
                  <div className="settings-header">
                    <h3>
                      Settings
                    </h3>
                  </div>

                  <div className="settings-content">
                    <div className="settings-group">
                      <label>
                        Theme
                      </label>

                      <div className="theme-options">
                        <button
                          className={`theme-option ${
                            theme ===
                            "light"
                              ? "active"
                              : ""
                          }`}
                          onClick={() =>
                            setTheme(
                              "light"
                            )
                          }
                        >
                          ☀️ Light
                        </button>

                        <button
                          className={`theme-option ${
                            theme ===
                            "dark"
                              ? "active"
                              : ""
                          }`}
                          onClick={() =>
                            setTheme(
                              "dark"
                            )
                          }
                        >
                          🌙 Dark
                        </button>
                      </div>
                    </div>

                    <div className="settings-group">
                      <label>
                        Information
                      </label>

                      <div className="info-box">
                        <p>
                          💾 Chat history is
                          saved locally
                        </p>

                        <p>
                          📌 Pin chats for
                          quick access
                        </p>

                        <p>
                          🔍 Search to find
                          conversations
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="header-status">
              <span className="online-dot"></span>
              Online
            </div>

            <div
              className="user-avatar"
              title="You"
            >
              U
            </div>
          </div>
        </header>

        {/* ==================================================
            CHAT
        ================================================== */}

        <main className="chat-container">
          <div className="messages">
            {/* ==================================================
                WELCOME
            ================================================== */}

            {messages.length ===
              0 && (
              <div className="welcome">
                <div className="welcome-icon">
                  🤖
                </div>

                <h2>
                  Good to see you! 👋
                </h2>

                <h3>
                  How can I assist you?
                </h3>

                <p>
                  Quickly find answers,
                  run office tasks, and get
                  real-time information — all
                  in one place.
                </p>

                <div className="suggestion-cards">
                  {suggestionCards.map(
                    (card) => (
                      <button
                        key={
                          card.title
                        }
                        className="suggestion-card"
                        onClick={() =>
                          setMessage(
                            card.prompt
                          )
                        }
                      >
                        <div className="suggestion-card-header">
                          <span className="suggestion-card-icon">
                            {
                              card.icon
                            }
                          </span>

                          <span className="suggestion-card-title">
                            {
                              card.title
                            }
                          </span>
                        </div>

                        <p className="suggestion-card-description">
                          {
                            card.description
                          }
                        </p>

                        <span className="suggestion-card-arrow">
                          Try it →
                        </span>
                      </button>
                    )
                  )}
                </div>

                {/* ==================================================
                    HERO INPUT
                ================================================== */}

                <div
                  className="hero-input-area"
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "stretch",
                    width: "100%",
                    boxSizing: "border-box",
                  }}
                >
                  {renderSelectedFiles()}

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      width: "100%",
                      minHeight: "58px",
                    }}
                  >
                    <button
                      type="button"
                      className="upload-button"
                      onClick={
                        openFilePicker
                      }
                      disabled={
                        loading ||
                        Boolean(
                          approval
                        ) ||
                        pendingUploads.length >
                          0
                      }
                    >
                      +
                    </button>

                    <textarea
                      value={
                        message
                      }
                      onChange={(
                        event
                      ) =>
                        setMessage(
                          event.target
                            .value
                        )
                      }
                      onKeyDown={
                        handleKeyDown
                      }
                      placeholder="Ask anything..."
                      rows="1"
                      disabled={
                        loading ||
                        Boolean(
                          approval
                        ) ||
                        pendingUploads.length >
                          0
                      }
                      style={{
                        flex: 1,
                        minWidth: 0,
                      }}
                    />

                    <button
                      className="hero-send-button"
                      onClick={
                        sendMessage
                      }
                      disabled={
                        !canSend
                      }
                    >
                      {loading
                        ? "..."
                        : "➤"}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* ==================================================
                MESSAGES
            ================================================== */}

            {messages.map(
              (item, index) => (
                <div
                  key={index}
                  className={`message-row ${item.role}`}
                >
                  <div
                    className={`avatar ${item.role}`}
                  >
                    {item.role ===
                    "user"
                      ? "U"
                      : "AI"}
                  </div>

                  <div
                    className={`message ${item.role}`}
                  >
                    <div className="role">
                      {item.role ===
                      "user"
                        ? "You"
                        : "Assistant"}
                    </div>

                    {item.timestamp && (
                      <div className="message-time">
                        {formatTime(
                          item.timestamp
                        )}
                      </div>
                    )}

                    <div className="content">
                      {
                        item.content
                      }
                    </div>

                    <button
                      className={`copy-button ${
                        copiedMessageId ===
                        index
                          ? "copied"
                          : ""
                      }`}
                      onClick={() =>
                        copyMessage(
                          item.content,
                          index
                        )
                      }
                    >
                      {copiedMessageId ===
                      index
                        ? "✓ Copied"
                        : "📋 Copy"}
                    </button>
                  </div>
                </div>
              )
            )}

            {/* ==================================================
                LOADING
            ================================================== */}

            {loading &&
              !approval &&
              pendingUploads.length ===
                0 && (
                <div className="message-row assistant">
                  <div className="avatar assistant">
                    AI
                  </div>

                  <div className="message assistant">
                    <div className="role">
                      Assistant
                    </div>

                    <div className="typing">
                      <span></span>
                      <span></span>
                      <span></span>

                      <span className="thinking-text">
                        Thinking...
                      </span>
                    </div>
                  </div>
                </div>
              )}

            {/* ==================================================
                DOCUMENT UPLOAD CONFIRMATION
            ================================================== */}

            {pendingUploads.length >
              0 && (
              <div className="upload-confirmation-card">
                <div className="upload-confirmation-icon">
                  📄
                </div>

                <div className="upload-confirmation-content">
                  <h2>
                    Document uploaded
                  </h2>

                  <p className="upload-confirmation-subtitle">
                    Your document is ready to use.
                  </p>

                  <div className="upload-confirmation-files">
                    {pendingUploads.map(
                      (pendingUpload) => (
                        <div
                          className="upload-confirmation-file"
                          key={
                            pendingUpload.pending_upload_id
                          }
                        >
                          <span>
                            📄
                          </span>

                          <strong
                            title={
                              pendingUpload.file_name
                            }
                          >
                            {
                              pendingUpload.file_name
                            }
                          </strong>
                        </div>
                      )
                    )}
                  </div>

                  <p className="upload-confirmation-message">
                    File uploaded successfully.
                    Do you want to save this
                    document permanently for
                    future conversations?
                  </p>

                  <div className="upload-confirmation-buttons">
                    <button
                      className="save-permanently-button"
                      disabled={
                        loading
                      }
                      onClick={() =>
                        handleUploadConfirmation(
                          true
                        )
                      }
                    >
                      {loading
                        ? "Processing..."
                        : "💾 Save Permanently"}
                    </button>

                    <button
                      className="use-chat-button"
                      disabled={
                        loading
                      }
                      onClick={() =>
                        handleUploadConfirmation(
                          false
                        )
                      }
                    >
                      {loading
                        ? "Processing..."
                        : "💬 Use Only This Chat"}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* ==================================================
                APPROVAL
            ================================================== */}

            {approval && (
              <div className="approval-card">
                <div className="approval-icon">
                  ⚠️
                </div>

                <div className="approval-content">
                  <h2>
                    Human Approval Required
                  </h2>

                  <p className="approval-message">
                    {approval.message ||
                      "This operation requires your confirmation before it can continue."}
                  </p>

                  <div className="approval-risk">
                    <span>
                      Risk Level
                    </span>

                    <strong>
                      {approval.risk ||
                        "HIGH"}
                    </strong>
                  </div>

                  <div className="approval-reason">
                    <strong>
                      Why approval is
                      required
                    </strong>

                    <p>
                      {approval.reason ||
                        "This action may have an external or irreversible effect."}
                    </p>
                  </div>

                  {approval.arguments && (
                    <div className="approval-details">
                      {approval
                        .arguments
                        .to && (
                        <div className="detail-row">
                          <span>
                            Recipient
                          </span>

                          <strong>
                            {
                              approval
                                .arguments
                                .to
                            }
                          </strong>
                        </div>
                      )}

                      {approval
                        .arguments
                        .subject && (
                        <div className="detail-row">
                          <span>
                            Subject
                          </span>

                          <strong>
                            {
                              approval
                                .arguments
                                .subject
                            }
                          </strong>
                        </div>
                      )}

                      {approval
                        .arguments
                        .body && (
                        <div className="message-preview">
                          <span>
                            Message
                            Preview
                          </span>

                          <div>
                            {
                              approval
                                .arguments
                                .body
                            }
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="approval-buttons">
                    <button
                      className="reject-button"
                      disabled={
                        loading
                      }
                      onClick={() =>
                        handleApproval(
                          false
                        )
                      }
                    >
                      ❌ Reject
                    </button>

                    <button
                      className="approve-button"
                      disabled={
                        loading
                      }
                      onClick={() =>
                        handleApproval(
                          true
                        )
                      }
                    >
                      {loading
                        ? "Processing..."
                        : "✅ Approve"}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ==================================================
              NORMAL INPUT
          ================================================== */}

          {messages.length >
            0 && (
            <div className="input-wrapper">
              <div
                className="input-area"
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "stretch",
                  width: "100%",
                  boxSizing: "border-box",
                }}
              >
                {renderSelectedFiles()}

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    width: "100%",
                    minHeight: "58px",
                  }}
                >
                  <button
                    type="button"
                    className="upload-button"
                    onClick={
                      openFilePicker
                    }
                    disabled={
                      loading ||
                      Boolean(
                        approval
                      ) ||
                      pendingUploads.length >
                        0
                    }
                  >
                    +
                  </button>

                  <textarea
                    value={
                      message
                    }
                    onChange={(
                      event
                    ) =>
                      setMessage(
                        event.target
                          .value
                      )
                    }
                    onKeyDown={
                      handleKeyDown
                    }
                    placeholder="Message your Office Assistant..."
                    rows="2"
                    disabled={
                      loading ||
                      Boolean(
                        approval
                      ) ||
                      pendingUploads.length >
                        0
                    }
                    style={{
                      flex: 1,
                      minWidth: 0,
                    }}
                  />

                  <button
                    className="send-button"
                    onClick={
                      sendMessage
                    }
                    disabled={
                      !canSend
                    }
                  >
                    {loading
                      ? "..."
                      : "➤"}
                  </button>
                </div>
              </div>

              <div className="input-hint">
                Press Enter to send ·
                Shift + Enter for a new
                line
              </div>
            </div>
          )}
        </main>
      </div>

      {/* ==================================================
          DELETE MODAL
      ================================================== */}

      {deleteChatId && (
        <div
          className="modal-overlay"
          onClick={
            cancelDelete
          }
        >
          <div
            className="delete-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="delete-icon">
              🗑️
            </div>

            <h2>
              Delete this chat?
            </h2>

            <p>
              This conversation will
              be removed from your chat
              history. This action cannot
              be undone.
            </p>

            <div className="delete-actions">
              <button
                className="cancel-delete"
                onClick={
                  cancelDelete
                }
              >
                Cancel
              </button>

              <button
                className="confirm-delete"
                onClick={
                  confirmDelete
                }
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;