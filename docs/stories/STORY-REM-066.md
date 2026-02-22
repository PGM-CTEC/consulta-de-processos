# STORY-REM-066: User Feedback Mechanism

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** Feature
**Complexity:** 3 pts (S - 1 day)
**Priority:** LOW
**Assignee:** Frontend Developer
**Status:** Ready
**Sprint:** Sprint 5+

## Description

Add user feedback mechanism (feedback button, survey link, or support email) to collect user input and bug reports.

## Acceptance Criteria

- [ ] Feedback button added to UI (floating action button)
- [ ] Feedback form created (name, email, message)
- [ ] Form submissions sent to support email or tracking system
- [ ] Thank you message displayed after submission
- [ ] Rate limiting to prevent spam
- [ ] Privacy notice included

## Technical Notes

```jsx
// FeedbackButton.jsx
import { useState } from 'react';

const FeedbackButton = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    await fetch('/api/feedback', {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(formData)),
      headers: { 'Content-Type': 'application/json' }
    });

    alert('Obrigado pelo seu feedback!');
    setIsOpen(false);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-indigo-600 text-white rounded-full p-4 shadow-lg hover:bg-indigo-700"
      >
        💬 Feedback
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md">
            <h2 className="text-xl font-bold mb-4">Envie seu feedback</h2>
            <form onSubmit={handleSubmit}>
              <input name="name" placeholder="Nome" className="w-full mb-2 p-2 border rounded" />
              <input name="email" type="email" placeholder="Email" className="w-full mb-2 p-2 border rounded" />
              <textarea name="message" placeholder="Mensagem" className="w-full mb-2 p-2 border rounded" rows="4"></textarea>
              <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded">Enviar</button>
              <button type="button" onClick={() => setIsOpen(false)} className="ml-2 px-4 py-2 rounded">Cancelar</button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
```

## Dependencies

None

## Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] Unit tests written (if applicable)
- [ ] Acceptance criteria met (all checkboxes ✅)
- [ ] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

_To be updated during development_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
