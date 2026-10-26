import { useState, useEffect } from "react"
import { apiRequest } from '../services/api'

function SupportWorkspace({ conversations }) {

  const [selectedId, setSelectedId] = useState(1)
  const [viewMode, setViewMode] = useState('agent')
  const [replyDraft, setReplyDraft] = useState(null)
  const [previousApprovedDraft, setPreviousApprovedDraft] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationError, setGenerationError] = useState('')
  const [messagesByConversation, setMessagesByConversation] = useState(() =>
    Object.fromEntries(
      conversations.map((conversation) => [
        conversation.id,
        conversation.messages ?? [],
      ]),
    ),
  )

  const [messageInput, setMessageInput] = useState('')
  const [editedReply, setEditedReply] = useState('')
  const [isSavingEdit, setIsSavingEdit] = useState(false)
  const [editError, setEditError] = useState('')
  const [editSaved, setEditSaved] = useState(false)
  const [isApproving, setIsApproving] = useState(false)
  const [approvalError, setApprovalError] = useState('')
  const [approvalSuccess, setApprovalSuccess] = useState(false)

  
  useEffect(() => {
    let cancelled = false

    async function loadLatestDraft() {
      setReplyDraft(null)
      setPreviousApprovedDraft(null)
      setEditedReply('')
      setGenerationError('')
      setEditError('')
      setEditSaved(false)
      setApprovalError('')
      setApprovalSuccess('')

      try {
        const draft = await apiRequest(
          `/reply-drafts/conversation/${selectedId}/latest`,
        )

        if (cancelled) return

        setReplyDraft(draft)
        setEditedReply(
          draft.edited_response ?? draft.ai_response ?? '',
        )
      } catch (error) {
        if (cancelled) return

        if (
          !error.message.includes('No reply draft found') &&
          !error.message.includes('404')
        ) {
          console.error('Failed to load saved reply draft:', error)
        }
      }

      try {
        const approvedDraft = await apiRequest(
          `/reply-drafts/conversation/${selectedId}/latest-approved`,
        )

        if (cancelled) return

        setPreviousApprovedDraft(approvedDraft)
      } catch (error) {
        if (cancelled) return

        if (
          !error.message.includes('No approved reply found') &&
          !error.message.includes('404')
        ) {
          console.error('Failed to load approved reply:', error)
        }
      }
    }

    loadLatestDraft()

    return () => {
      cancelled = true
    }
  }, [selectedId])

  const selectedConversation =
    conversations.find((conversation) => conversation.id === selectedId) ??
    conversations[0]

    
  
  async function handleSendMessage(event) {
    event.preventDefault()

    const content = messageInput.trim()
    if (!content) return

    try {
      const savedMessage = await apiRequest(
        `/conversations/${selectedId}/messages/`,
        {
          method: 'POST',
          body: JSON.stringify({
            sender_type: viewMode,
            content,
          }),
        },
      )

      setMessagesByConversation((previous) => ({
        ...previous,
        [selectedId]: [
          ...(previous[selectedId] ?? []),
          {
            id: savedMessage.id,
            sender: savedMessage.sender_type,
            content: savedMessage.content,
          },
        ],
      }))

      setMessageInput('')
    } catch (error) {
      console.error('Failed to send message:', error)
      window.alert(`Could not save message: ${error.message}`)
    }
  }



  
  async function handleGenerateReply() {
    setIsGenerating(true)
    setGenerationError('')

    try {
      const draft = await apiRequest(
        `/reply-drafts/generate/${selectedId}`,
        { method: 'POST' },
      )

      if (replyDraft?.status === 'approved') {
        setPreviousApprovedDraft(replyDraft)
      }

      setReplyDraft(draft)
      setEditedReply(draft.edited_response ?? draft.ai_response)
      setEditError('')
      setEditSaved(false)
    } catch (error) {
      console.error('Failed to generate AI reply:', error)
      setGenerationError(error.message)
    } finally {
      setIsGenerating(false)
    }
  }




  async function handleSaveEdit() {
    if (!replyDraft || !editedReply.trim()) return

    setIsSavingEdit(true)
    setEditError('')
    setEditSaved(false)

    try {
      const updatedDraft = await apiRequest(
        `/reply-drafts/${replyDraft.id}`,
        {
          method: 'PUT',
          body: JSON.stringify({
            edited_response: editedReply.trim(),
          }),
        },
      )

      setReplyDraft(updatedDraft)
      setEditedReply(updatedDraft.edited_response ?? '')
      setEditSaved(true)
    } catch (error) {
      console.error('Failed to save edited reply:', error)
      setEditError(error.message)
    } finally {
      setIsSavingEdit(false)
    }
  }



  async function handleApproveReply() {
    if (!replyDraft || replyDraft.status !== 'draft') return

    setIsApproving(true)
    setApprovalError('')
    setApprovalSuccess(false)

    try {
      const approvedDraft = await apiRequest(
        `/reply-drafts/${replyDraft.id}/approve`,
        { method: 'POST' },
      )

      setReplyDraft(approvedDraft)
      setEditedReply(
        approvedDraft.final_response ??
        approvedDraft.edited_response ??
        approvedDraft.ai_response,
      )
      setApprovalSuccess(true)
    } catch (error) {
      console.error('Failed to approve reply:', error)
      setApprovalError(error.message)
    } finally {
      setIsApproving(false)
    }
  }


  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-8 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
            Datastraw
          </p>
          <h1 className="mt-1 text-xl font-bold">CX Reply Assistant</h1>
        </div>

        <div className="flex items-center gap-3">
          <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700">
            ● System ready
          </span>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 font-semibold text-indigo-700">
            A
          </div>
        </div>
      </header>

      <div className="grid min-h-[calc(100vh-73px)] grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)]">
        <aside className="border-r border-slate-200 bg-white p-5">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="font-semibold">Conversations</h2>
            <span className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600">
              {conversations.length} total
            </span>
          </div>

          <label className="mb-4 block">
            <span className="sr-only">Search conversations</span>
            <input
              type="search"
              placeholder="Search conversations..."
              className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            />
          </label>

          <div className="space-y-2">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                onClick={() => setSelectedId(conversation.id)}
                className={`w-full rounded-xl border p-3 text-left transition ${
                  selectedId === conversation.id
                    ? 'border-indigo-200 bg-indigo-50'
                    : 'border-transparent hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="font-semibold">{conversation.name}</span>
                  <span className="whitespace-nowrap text-xs text-slate-500">
                    {conversation.time}
                  </span>
                </div>
                <p className="mt-1 text-xs font-medium text-indigo-600">
                  {conversation.brand}
                </p>
                <p className="mt-2 line-clamp-2 text-sm leading-5 text-slate-600">
                  {conversation.preview}
                </p>
              </button>
            ))}
          </div>
        </aside>

        <section className="p-5 md:p-8">
          <div className="mb-6">
            <p className="text-sm text-slate-500">Customer support / Inbox</p>
            <h2 className="mt-1 text-2xl font-bold">Good morning, Agent</h2>
            <p className="mt-1 text-sm text-slate-600">
              Review conversations and prepare policy-aware customer replies.
            </p>
          </div>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-200 p-5">
                <div>
                  <h3 className="font-semibold">{selectedConversation.name}</h3>
                  <p className="mt-1 text-sm text-slate-500">
                    {selectedConversation.brand} · Conversation #{selectedConversation.id}
                  </p>
                </div>
                <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
                  Open
                </span>
              </div>

              
              <div className="flex items-center justify-between border-b border-slate-200 bg-white px-5 py-3">
                <span className="text-sm font-medium text-slate-600">
                  Viewing conversation as
                </span>

                <div className="flex rounded-lg bg-slate-100 p-1">
                  <button
                    type="button"
                    onClick={() => setViewMode('customer')}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      viewMode === 'customer'
                        ? 'bg-white text-indigo-700 shadow-sm'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    Customer
                  </button>

                  <button
                    type="button"
                    onClick={() => setViewMode('agent')}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      viewMode === 'agent'
                        ? 'bg-white text-indigo-700 shadow-sm'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    Agent
                  </button>
                </div>
              </div>

              <div className="space-y-5 bg-slate-50/70 p-5">
                {(messagesByConversation[selectedId] ?? []).map((message) => {
                  const isCustomer = message.sender === 'customer'

                  return (
                    <div
                      key={message.id}
                      className={`max-w-[85%] rounded-2xl border p-4 shadow-sm ${
                        isCustomer
                          ? 'rounded-tl-sm border-slate-200 bg-white'
                          : 'ml-auto rounded-tr-sm border-indigo-600 bg-indigo-600 text-white'
                      }`}
                    >
                      <p
                        className={`mb-2 text-xs font-semibold ${
                          isCustomer ? 'text-slate-500' : 'text-indigo-100'
                        }`}
                      >
                        {isCustomer ? `${selectedConversation.name} · Customer` : 'Support agent'}
                      </p>

                      <p className="text-sm leading-6">{message.content}</p>
                    </div>
                  )
                })}
              </div>

              
              <form
                onSubmit={handleSendMessage}
                className="border-t border-slate-200 bg-white p-4"
              >
                <p className="mb-3 text-xs text-slate-500">
                  Sending as{' '}
                  <span className="font-semibold text-indigo-600">
                    {viewMode === 'customer' ? 'Customer' : 'Support agent'}
                  </span>
                </p>

                <div className="flex items-end gap-3">
                  <label className="flex-1">
                    <span className="sr-only">Write a message</span>
                    <textarea
                      value={messageInput}
                      onChange={(event) => setMessageInput(event.target.value)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' && !event.shiftKey) {
                          event.preventDefault()
                          event.currentTarget.form?.requestSubmit()
                        }
                      }}
                      placeholder={`Write a message as ${viewMode}...`}
                      rows={2}
                      className="w-full resize-y rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                    />
                  </label>

                  <button
                    type="submit"
                    disabled={!messageInput.trim()}
                    className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Send
                  </button>
                </div>

                <p className="mt-2 text-xs text-slate-400">
                  Press Enter to send · Shift + Enter for a new line
                </p>
              </form>

            </section>

            <aside className="space-y-4">
              <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <h3 className="font-semibold">Order details</h3>
                <p className="mt-1 text-sm text-slate-500">{selectedConversation.orderNumber}</p>
                <div className="my-4 border-t border-slate-100" />
                <p className="text-sm text-slate-500">Product</p>
                <p className="mt-1 text-sm font-medium">
                  {selectedConversation.product}
                </p>
                <p className="mt-4 text-sm text-slate-500">Order status</p>
                <span className="mt-1 inline-block rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                  {selectedConversation.orderStatus}
                </span>
              </section>

              <section className="rounded-2xl border border-indigo-100 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                    ✦
                  </span>
                  <div>
                    <h3 className="font-semibold">AI Reply Assistant</h3>
                    <p className="text-xs text-slate-500">Policy-aware drafts</p>
                  </div>
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-600">
                  Generate a reply using the selected brand’s policies and the
                  conversation context.
                </p>
                
                <button
                  type="button"
                  onClick={handleGenerateReply}
                  disabled={isGenerating}
                  className="mt-4 w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isGenerating
                    ? 'Generating reply...'
                    : replyDraft
                      ? 'Regenerate reply'
                      : 'Generate AI reply'}
                </button>

                {generationError && (
                  <p role="alert" className="mt-3 text-sm text-red-600">
                    {generationError}
                  </p>
                )}


                {previousApprovedDraft &&
                  previousApprovedDraft.id !== replyDraft?.id && (
                    <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
                      <h4 className="text-sm font-semibold text-emerald-800">
                        Previously approved response
                      </h4>

                      <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-emerald-900">
                        {previousApprovedDraft.final_response}
                      </p>

                      <p className="mt-3 text-xs font-medium text-emerald-700">
                        Approved · Preserved when generating a new draft
                      </p>
                    </div>
                  )}


                {replyDraft && (
                  <div className="mt-5 space-y-4">
                    
                    <div>
                      <h4 className="text-sm font-semibold text-slate-800">
                        {replyDraft.status === 'approved'
                          ? 'Original AI-generated reply'
                          : 'Generated reply'}
                      </h4>

                      <div className="mt-2 rounded-xl border border-indigo-100 bg-indigo-50 p-4">
                        <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
                          {replyDraft.ai_response}
                        </p>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-slate-800">
                        Edit reply
                      </h4>

                      <textarea
                        value={editedReply}
                        disabled={replyDraft.status === 'approved'}
                        onChange={(event) => {
                          setEditedReply(event.target.value)
                          setEditSaved(false)
                          setEditError('')
                        }}
                        rows={7}
                        className="mt-2 w-full resize-y rounded-xl border border-slate-200 bg-white p-3 text-sm leading-6 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                      />

                      {replyDraft.status === 'draft' && (
                        <button
                          type="button"
                          disabled={isSavingEdit || !editedReply.trim()}
                          onClick={handleSaveEdit}
                          className="mt-3 w-full rounded-lg border border-indigo-200 bg-white px-4 py-2.5 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {isSavingEdit ? 'Saving changes...' : 'Save edited reply'}
                        </button>
                      )}

                      {editError && (
                        <p role="alert" className="mt-2 text-sm text-red-600">
                          {editError}
                        </p>
                      )}

                      {editSaved && (
                        <p className="mt-2 text-sm text-emerald-700">
                          Edited reply saved successfully.
                        </p>
                      )}

                      <button
                        type="button"
                        onClick={handleApproveReply}
                        disabled={
                          isApproving ||
                          replyDraft.status !== 'draft' ||
                          !editedReply.trim()
                        }
                        className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isApproving
                          ? 'Approving...'
                          : replyDraft.status === 'approved'
                            ? 'Reply approved'
                            : 'Approve final reply'}
                      </button>

                      {approvalError && (
                        <p role="alert" className="mt-2 text-sm text-red-600">
                          {approvalError}
                        </p>
                      )}

                      {approvalSuccess && (
                        <p className="mt-2 text-sm text-emerald-700">
                          Final reply approved and saved.
                        </p>
                      )}

                    </div>

                    {replyDraft.status === 'approved' && (
                      <div>
                        <h4 className="text-sm font-semibold text-slate-800">
                          Approved final response
                        </h4>

                        <div className="mt-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
                          <p className="whitespace-pre-wrap text-sm leading-6 text-emerald-900">
                            {replyDraft.final_response}
                          </p>
                        </div>
                      </div>
                    )}

                    <div>
                      <h4 className="text-sm font-semibold text-slate-800">
                        Retrieved policy context
                      </h4>

                      <div className="mt-2 rounded-xl border border-slate-200 bg-slate-50 p-4">
                        <p className="whitespace-pre-wrap text-sm leading-6 text-slate-600">
                          {replyDraft.retrieved_context || 'No relevant policy was found.'}
                        </p>
                      </div>
                    </div>

                  </div>
                )}

              </section>
            </aside>
          </div>
        </section>
      </div>

    </main>
  )
}

export default SupportWorkspace
