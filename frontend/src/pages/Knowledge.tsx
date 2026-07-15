import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { BookOpen, Plus, Loader2, Trash2 } from "lucide-react";
import { knowledgeApi, ApiError } from "../services/api";
import type { KnowledgeArticle } from "../types";

const EMPTY_FORM = { title: "", content: "", category: "General", tags: "" };

export default function Knowledge() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [selected, setSelected] = useState<KnowledgeArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [searchQ, setSearchQ] = useState("");
  const [error, setError] = useState("");

  const fetchArticles = useCallback(async () => {
    try {
      const data = searchQ
        ? await knowledgeApi.search(searchQ)
        : await knowledgeApi.list();
      setArticles(data.articles);
      if (data.articles.length && !selected) setSelected(data.articles[0]);
    } catch {
      setError("Failed to load knowledge base");
    } finally {
      setLoading(false);
    }
  }, [searchQ]);

  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const article = await knowledgeApi.create({
        title: form.title,
        content: form.content,
        category: form.category,
        tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
      });
      setShowForm(false);
      setForm(EMPTY_FORM);
      setSelected(article);
      await fetchArticles();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Create failed");
    }
  };

  const handleDelete = async (id: string) => {
    await knowledgeApi.delete(id);
    setSelected(null);
    fetchArticles();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">Knowledge Base</h2>
          <p className="mt-1 text-sm text-gray-400">Security runbooks and troubleshooting articles.</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          <Plus className="h-4 w-4" /> New Article
        </button>
      </div>

      {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="card space-y-3">
          <input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input-field" placeholder="Title" />
          <input required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="input-field" placeholder="Category" />
          <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} className="input-field" placeholder="Tags (comma-separated)" />
          <textarea required value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} className="input-field min-h-[160px] font-mono text-sm" placeholder="Markdown content..." />
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-1">
          <input
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchArticles()}
            placeholder="Search articles..."
            className="input-field mb-3 text-sm"
          />
          {loading ? (
            <Loader2 className="mx-auto h-6 w-6 animate-spin text-sky-400" />
          ) : (
            <div className="max-h-[28rem] space-y-1 overflow-y-auto">
              {articles.map((a) => (
                <button
                  key={a.article_id}
                  onClick={() => setSelected(a)}
                  className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                    selected?.article_id === a.article_id ? "bg-sky-500/10 text-sky-400" : "hover:bg-surface-hover text-gray-300"
                  }`}
                >
                  <p className="font-medium truncate">{a.title}</p>
                  <p className="text-xs text-gray-500">{a.category}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="card lg:col-span-2">
          {selected ? (
            <>
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <span className="font-mono text-xs text-sky-400">{selected.article_id}</span>
                  <h3 className="text-lg font-semibold text-gray-100">{selected.title}</h3>
                  <div className="mt-1 flex flex-wrap gap-2">
                    <span className="rounded bg-surface-hover px-2 py-0.5 text-xs text-gray-400">{selected.category}</span>
                    {selected.tags.map((t) => (
                      <span key={t} className="rounded bg-sky-500/10 px-2 py-0.5 text-xs text-sky-400">{t}</span>
                    ))}
                    {selected.incident_ref && (
                      <span className="rounded bg-red-500/10 px-2 py-0.5 text-xs text-red-400">{selected.incident_ref}</span>
                    )}
                  </div>
                </div>
                <button onClick={() => handleDelete(selected.article_id)} className="btn-secondary p-2 text-red-400">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <article className="prose prose-invert prose-sm max-w-none prose-headings:text-gray-100 prose-p:text-gray-300 prose-li:text-gray-300">
                <ReactMarkdown>{selected.content}</ReactMarkdown>
              </article>
            </>
          ) : (
            <div className="py-16 text-center">
              <BookOpen className="mx-auto h-10 w-10 text-gray-600" />
              <p className="mt-3 text-sm text-gray-500">Select or create an article</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
