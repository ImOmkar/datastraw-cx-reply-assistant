
// import { useEffect, useState } from 'react'
// import { apiRequest } from './services/api'
// import SupportWorkspace from './pages/SupportWorkspace'

// function App() {
//   const [apiStatus, setApiStatus] = useState('Loading conversations...')
//   const [conversations, setConversations] = useState([])

//   useEffect(() => {
//     async function loadConversations() {
//       try {
        
//         const [brands, data] = await Promise.all([
//           apiRequest('/brands/'),
//           apiRequest('/conversations/'),
//         ])

//         const brandNames = Object.fromEntries(
//           brands.map((brand) => [brand.id, brand.name]),
//         )

//         const mappedConversations = await Promise.all(
//           data.map(async (conversation) => {
//             const messages = await apiRequest(
//               `/conversations/${conversation.id}/messages/`,
//             )

//             return {
//               id: conversation.id,
//               name: conversation.customer_name,
//               brand: brandNames[conversation.brand_id] ?? 'Unknown brand',
//               preview: messages.at(-1)?.content ?? conversation.order_details,
//               time: '',
//               orderNumber: conversation.order_number ?? 'Not provided',
//               orderStatus: conversation.order_status,
//               product: conversation.order_details,
//               messages: messages.map((message) => ({
//                 id: message.id,
//                 sender: message.sender_type,
//                 content: message.content,
//               })),
//             }
//           }),
//         )
//         setConversations(mappedConversations)
//         setApiStatus(`Connected — ${mappedConversations.length} conversations loaded`)
//       } catch (error) {
//         console.error('Failed to load workspace data:', error)
//         setApiStatus(`Failed to load conversations: ${error.message}`)
//         setConversations([])
//       }
//     }

//     loadConversations()
//   }, [])

//   return (
//     <>
//       <div className="border-b border-slate-200 bg-white px-5 py-2 text-sm">
//         Backend status: {apiStatus}
//       </div>

//       {conversations.length > 0 ? (
//         <SupportWorkspace conversations={conversations} />
//       ) : (
//         <div className="p-8 text-sm text-slate-600">{apiStatus}</div>
//       )}
//     </>
//   )
// }

// export default App



// import KnowledgeBase from './pages/KnowledgeBase'

// function App() {
//   return <KnowledgeBase />
// }

// export default App



import { useEffect, useState } from 'react'
import { apiRequest } from './services/api'
import SupportWorkspace from './pages/SupportWorkspace'
import KnowledgeBase from './pages/KnowledgeBase'

function App() {
  const [apiStatus, setApiStatus] = useState('Checking backend...')
  const [conversations, setConversations] = useState([])
  const [activePage, setActivePage] = useState('support')

  useEffect(() => {
    async function loadConversations() {
      try {
        const [brands, data] = await Promise.all([
          apiRequest('/brands/'),
          apiRequest('/conversations/'),
        ])

        const brandNames = Object.fromEntries(
          brands.map((brand) => [brand.id, brand.name]),
        )

        const mappedConversations = await Promise.all(
          data.map(async (conversation) => {
            const messages = await apiRequest(
              `/conversations/${conversation.id}/messages/`,
            )

            return {
              id: conversation.id,
              name: conversation.customer_name,
              brand: brandNames[conversation.brand_id] ?? 'Unknown brand',
              preview: messages.at(-1)?.content ?? conversation.order_details,
              time: '',
              orderNumber: conversation.order_number ?? 'Not provided',
              orderStatus: conversation.order_status,
              product: conversation.order_details,
              messages: messages.map((message) => ({
                id: message.id,
                sender: message.sender_type,
                content: message.content,
              })),
            }
          }),
        )

        setConversations(mappedConversations)
        setApiStatus(
          `Connected — ${mappedConversations.length} conversations loaded`,
        )
      } catch (error) {
        console.error('Failed to load workspace data:', error)
        setApiStatus(`Failed to load conversations: ${error.message}`)
        setConversations([])
      }
    }

    loadConversations()
  }, [])

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-5 py-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
            Datastraw
          </p>
          <p className="text-sm text-slate-500">{apiStatus}</p>
        </div>

        <nav className="flex gap-2" aria-label="Main navigation">
          <button
            type="button"
            onClick={() => setActivePage('support')}
            className={`rounded-lg px-4 py-2 text-sm font-semibold ${
              activePage === 'support'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Support Inbox
          </button>

          <button
            type="button"
            onClick={() => setActivePage('knowledge')}
            className={`rounded-lg px-4 py-2 text-sm font-semibold ${
              activePage === 'knowledge'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Knowledge Base
          </button>
        </nav>
      </div>

      {activePage === 'support' ? (
        conversations.length > 0 ? (
          <SupportWorkspace conversations={conversations} />
        ) : (
          <p className="p-8 text-sm text-slate-600">{apiStatus}</p>
        )
      ) : (
        <KnowledgeBase />
      )}
    </div>
  )
}

export default App
