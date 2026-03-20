import React, { useState } from 'react';
import { MessageSquare, X, Send, CheckCircle } from 'lucide-react';

const FEEDBACK_EMAIL = 'suporte@pgm-rio.gov.br';

function FeedbackButton() {
    const [open, setOpen] = useState(false);
    const [form, setForm] = useState({ name: '', email: '', message: '' });
    const [sent, setSent] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);

        // Build mailto link as fallback (no backend required)
        const subject = encodeURIComponent('Feedback — Consulta Processual');
        const body = encodeURIComponent(
            `Nome: ${form.name}\nEmail: ${form.email}\n\nMensagem:\n${form.message}`
        );
        window.open(`mailto:${FEEDBACK_EMAIL}?subject=${subject}&body=${body}`, '_blank');

        setSent(true);
        setSubmitting(false);
        setTimeout(() => {
            setSent(false);
            setOpen(false);
            setForm({ name: '', email: '', message: '' });
        }, 3000);
    };

    return (
        <>
            {/* Floating Action Button */}
            <button
                onClick={() => setOpen(true)}
                aria-label="Enviar feedback"
                className="fixed bottom-6 right-6 z-50 bg-indigo-600 text-white rounded-full p-3 shadow-lg hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
                <MessageSquare className="h-5 w-5" aria-hidden="true" />
            </button>

            {/* Feedback Modal */}
            {open && (
                <div
                    role="dialog"
                    aria-modal="true"
                    aria-label="Formulário de feedback"
                    className="fixed inset-0 z-50 flex items-end justify-end p-6"
                >
                    <div className="bg-white rounded-xl shadow-2xl w-80 border border-gray-100">
                        <div className="flex items-center justify-between p-4 border-b border-gray-100">
                            <h2 className="font-semibold text-gray-900 text-sm">Enviar Feedback</h2>
                            <button onClick={() => setOpen(false)} aria-label="Fechar" className="text-gray-400 hover:text-gray-600">
                                <X className="h-4 w-4" />
                            </button>
                        </div>

                        {sent ? (
                            <div className="p-6 text-center">
                                <CheckCircle className="h-10 w-10 text-green-500 mx-auto mb-2" />
                                <p className="text-sm font-medium text-gray-800">Obrigado pelo feedback!</p>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="p-4 space-y-3">
                                <input
                                    type="text"
                                    placeholder="Nome (opcional)"
                                    value={form.name}
                                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 focus:border-transparent outline-none"
                                />
                                <input
                                    type="email"
                                    placeholder="Email (opcional)"
                                    value={form.email}
                                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 focus:border-transparent outline-none"
                                />
                                <textarea
                                    required
                                    rows={3}
                                    placeholder="Sua mensagem..."
                                    value={form.message}
                                    onChange={e => setForm(f => ({ ...f, message: e.target.value }))}
                                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 focus:border-transparent outline-none resize-none"
                                />
                                <p className="text-xs text-gray-400">
                                    Seu feedback será enviado para {FEEDBACK_EMAIL}. Nenhum dado sensível é coletado.
                                </p>
                                <button
                                    type="submit"
                                    disabled={submitting || !form.message.trim()}
                                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white text-sm font-medium py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    <Send className="h-4 w-4" />
                                    Enviar Feedback
                                </button>
                            </form>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}

export default FeedbackButton;
