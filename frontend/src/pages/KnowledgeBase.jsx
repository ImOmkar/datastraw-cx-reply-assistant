
import { useEffect, useState } from 'react'
import { apiRequest } from '../services/api'

function KnowledgeBase() {
    const [brands, setBrands] = useState([])
    const [selectedBrandId, setSelectedBrandId] = useState('')
    const [entries, setEntries] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    const [showCreateForm, setShowCreateForm] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [formError, setFormError] = useState('')
    const [formData, setFormData] = useState({
        title: '',
        category: 'returns',
        content: '',
    })

    const [editingEntryId, setEditingEntryId] = useState(null)
    const [editFormData, setEditFormData] = useState({
        title: '',
        category: '',
        content: '',
    })
    const [isUpdating, setIsUpdating] = useState(false)
    const [editError, setEditError] = useState('')
    const [deactivatingEntryId, setDeactivatingEntryId] = useState(null)
    const [deactivationError, setDeactivationError] = useState('')

    async function loadBrands() {
        try {
            const data = await apiRequest('/brands/')
            setBrands(data)

            if (data.length > 0) {
                setSelectedBrandId((current) => current || String(data[0].id))
            }
        } catch (err) {
            setError(`Could not load brands: ${err.message}`)
        }
    }

    async function loadEntries(brandId) {
        if (!brandId) return

        setIsLoading(true)
        setError('')

        try {
            const data = await apiRequest(`/knowledge-base/brand/${brandId}`)
            setEntries(data)
        } catch (err) {
            setError(`Could not load policies: ${err.message}`)
        } finally {
            setIsLoading(false)
        }
    }


    async function handleCreateEntry(event) {
        event.preventDefault()

        if (!selectedBrandId) {
            setFormError('Please select a brand.')
            return
        }

        setIsSaving(true)
        setFormError('')

        try {
            await apiRequest('/knowledge-base/', {
                method: 'POST',
                body: JSON.stringify({
                    brand_id: Number(selectedBrandId),
                    title: formData.title.trim(),
                    category: formData.category.trim(),
                    content: formData.content.trim(),
                }),
            })

            setFormData({
                title: '',
                category: 'returns',
                content: '',
            })
            setShowCreateForm(false)
            await loadEntries(selectedBrandId)
        } catch (err) {
            setFormError(`Could not save policy: ${err.message}`)
        } finally {
            setIsSaving(false)
        }
    }


    async function handleUpdateEntry(event) {
        event.preventDefault()

        if (!editingEntryId) return

        setIsUpdating(true)
        setEditError('')

        try {
            await apiRequest(`/knowledge-base/${editingEntryId}`, {
                method: 'PUT',
                body: JSON.stringify({
                    title: editFormData.title.trim(),
                    category: editFormData.category.trim(),
                    content: editFormData.content.trim(),
                }),
            })

            setEditingEntryId(null)
            setEditFormData({ title: '', category: '', content: '' })
            await loadEntries(selectedBrandId)
        } catch (err) {
            setEditError(`Could not update policy: ${err.message}`)
        } finally {
            setIsUpdating(false)
        }
    }


    async function handleDeactivateEntry(entryId) {
        const confirmed = window.confirm(
            'Deactivate this policy? It will no longer appear in the active policy list or be used for reply generation.',
        )

        if (!confirmed) return

        setDeactivatingEntryId(entryId)
        setDeactivationError('')

        try {
            await apiRequest(`/knowledge-base/${entryId}/deactivate`, {
                method: 'PATCH',
            })

            if (editingEntryId === entryId) {
                setEditingEntryId(null)
            }

            await loadEntries(selectedBrandId)
        } catch (err) {
            setDeactivationError(`Could not deactivate policy: ${err.message}`)
        } finally {
            setDeactivatingEntryId(null)
        }
    }


    useEffect(() => {
        loadBrands()
    }, [])

    useEffect(() => {
        loadEntries(selectedBrandId)
    }, [selectedBrandId])

    return (
        <main className="min-h-screen bg-slate-100 text-slate-900">
            <header className="border-b border-slate-200 bg-white px-8 py-5">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
                    Datastraw
                </p>
                <h1 className="mt-1 text-2xl font-bold">Knowledge Base</h1>
                <p className="mt-1 text-sm text-slate-500">
                    Manage support policies for each brand.
                </p>
            </header>

            <div className="mx-auto max-w-5xl p-5 md:p-8">
                <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                    <label className="block text-sm font-semibold">
                        Select brand
                        <select
                            value={selectedBrandId}
                            onChange={(event) => setSelectedBrandId(event.target.value)}
                            className="mt-2 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                        >
                            {brands.map((brand) => (
                                <option key={brand.id} value={String(brand.id)}>
                                    {brand.name}
                                </option>
                            ))}
                        </select>
                    </label>
                </section>


                <div className="mb-4 mt-8 flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h2 className="text-lg font-bold">Policy entries</h2>
                        <p className="mt-1 text-sm text-slate-500">
                            {entries.length} active {entries.length === 1 ? 'entry' : 'entries'}
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={() => {
                            setFormError('')
                            setShowCreateForm((current) => !current)
                        }}
                        className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
                    >
                        {showCreateForm ? 'Cancel' : '+ New policy'}
                    </button>
                </div>


                {showCreateForm && (
                    <form
                        onSubmit={handleCreateEntry}
                        className="mb-6 space-y-4 rounded-2xl border border-indigo-100 bg-white p-5 shadow-sm"
                    >
                        <h3 className="font-semibold">Create policy entry</h3>

                        <label className="block text-sm font-medium">
                            Policy title
                            <input
                                required
                                minLength={2}
                                maxLength={200}
                                value={formData.title}
                                onChange={(event) =>
                                    setFormData((current) => ({
                                        ...current,
                                        title: event.target.value,
                                    }))
                                }
                                placeholder="e.g. Damaged Item Returns"
                                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 font-normal outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                            />
                        </label>

                        <label className="block text-sm font-medium">
                            Category
                            <select
                                value={formData.category}
                                onChange={(event) =>
                                    setFormData((current) => ({
                                        ...current,
                                        category: event.target.value,
                                    }))
                                }
                                className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-indigo-400"
                            >
                                <option value="returns">Returns</option>
                                <option value="refunds">Refunds</option>
                                <option value="shipping">Shipping and delivery</option>
                                <option value="cancellation">Cancellations</option>
                                <option value="warranty">Warranty</option>
                                <option value="general">General support</option>
                            </select>
                        </label>

                        <label className="block text-sm font-medium">
                            Policy content
                            <textarea
                                required
                                minLength={10}
                                rows={5}
                                value={formData.content}
                                onChange={(event) =>
                                    setFormData((current) => ({
                                        ...current,
                                        content: event.target.value,
                                    }))
                                }
                                placeholder="Describe the policy, conditions, deadlines, and required evidence..."
                                className="mt-2 w-full resize-y rounded-lg border border-slate-200 px-3 py-2.5 font-normal leading-6 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                            />
                        </label>

                        {formError && (
                            <p role="alert" className="text-sm text-red-600">
                                {formError}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={isSaving || !selectedBrandId}
                            className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {isSaving ? 'Saving policy...' : 'Save policy'}
                        </button>
                    </form>
                )}


                {error && (
                    <p role="alert" className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                        {error}
                    </p>
                )}


                {deactivationError && (
                    <p role="alert" className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                        {deactivationError}
                    </p>
                )}


                {isLoading ? (
                    <p className="py-8 text-sm text-slate-500">Loading policies...</p>
                ) : entries.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
                        No active policy entries found for this brand.
                    </div>
                ) : (
                    <div className="space-y-4">
                        {entries.map((entry) => (
                            <article
                                key={entry.id}
                                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
                            >

                                <div className="flex flex-wrap items-start justify-between gap-3">
                                    <div>
                                        <h3 className="font-semibold">{entry.title}</h3>
                                        <span className="mt-2 inline-block rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700">
                                            {entry.category}
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <span className="text-xs text-slate-400">
                                            Policy #{entry.id}
                                        </span>

                                        <button
                                            type="button"
                                            onClick={() => {
                                                setEditingEntryId(entry.id)
                                                setEditFormData({
                                                    title: entry.title,
                                                    category: entry.category,
                                                    content: entry.content,
                                                })
                                                setEditError('')
                                                setShowCreateForm(false)
                                            }}
                                            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                                        >
                                            Edit
                                        </button>


                                        <button
                                            type="button"
                                            onClick={() => handleDeactivateEntry(entry.id)}
                                            disabled={deactivatingEntryId === entry.id}
                                            className="rounded-lg border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                                        >
                                            {deactivatingEntryId === entry.id ? 'Deactivating...' : 'Deactivate'}
                                        </button>

                                    </div>
                                </div>



                                {editingEntryId === entry.id ? (
                                    <form
                                        onSubmit={handleUpdateEntry}
                                        className="mt-4 space-y-4 border-t border-slate-100 pt-4"
                                    >
                                        <label className="block text-sm font-medium">
                                            Policy title
                                            <input
                                                required
                                                minLength={2}
                                                maxLength={200}
                                                value={editFormData.title}
                                                onChange={(event) =>
                                                    setEditFormData((current) => ({
                                                        ...current,
                                                        title: event.target.value,
                                                    }))
                                                }
                                                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal"
                                            />
                                        </label>

                                        <label className="block text-sm font-medium">
                                            Category
                                            <select
                                                value={editFormData.category}
                                                onChange={(event) =>
                                                    setEditFormData((current) => ({
                                                        ...current,
                                                        category: event.target.value,
                                                    }))
                                                }
                                                className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-normal"
                                            >
                                                <option value="returns">Returns</option>
                                                <option value="refunds">Refunds</option>
                                                <option value="shipping">Shipping and delivery</option>
                                                <option value="cancellation">Cancellations</option>
                                                <option value="warranty">Warranty</option>
                                                <option value="general">General support</option>
                                            </select>
                                        </label>

                                        <label className="block text-sm font-medium">
                                            Policy content
                                            <textarea
                                                required
                                                minLength={10}
                                                rows={5}
                                                value={editFormData.content}
                                                onChange={(event) =>
                                                    setEditFormData((current) => ({
                                                        ...current,
                                                        content: event.target.value,
                                                    }))
                                                }
                                                className="mt-2 w-full resize-y rounded-lg border border-slate-200 px-3 py-2 font-normal leading-6"
                                            />
                                        </label>

                                        {editError && (
                                            <p role="alert" className="text-sm text-red-600">
                                                {editError}
                                            </p>
                                        )}

                                        <div className="flex gap-3">
                                            <button
                                                type="submit"
                                                disabled={isUpdating}
                                                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                                            >
                                                {isUpdating ? 'Saving...' : 'Save changes'}
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setEditingEntryId(null)
                                                    setEditError('')
                                                }}
                                                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </form>
                                ) : (
                                    <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-600">
                                        {entry.content}
                                    </p>
                                )}

                            </article>
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}

export default KnowledgeBase
