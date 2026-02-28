# Ralph Loop — Implementar Stories Pendentes

Você é um desenvolvedor full-stack. Sua missão é implementar as stories pendentes deste projeto em ordem crescente de complexidade, uma por vez, até todas estarem concluídas.

## Ordem de Implementação

Implemente as stories nesta ordem (menor para maior):

1. REM-059 (XS) — README and Documentation Updates
2. REM-062 (XS) — Loading State Consistency
3. REM-064 (XS) — Favicon and Branding
4. REM-041 (S) — Analytics/Telemetry
5. REM-043 (S) — Soft Deletes
6. REM-044 (S) — SearchHistory Foreign Key
7. REM-046 (S) — Denormalized Court Cleanup
8. REM-047 (S) — API Versioning Strategy
9. REM-058 (S) — Update Dependencies to Latest Versions
10. REM-061 (S) — Error Messages Improvement
11. REM-066 (S) — User Feedback Mechanism
12. REM-048 (M) — Log Structure Improvement
13. REM-052 (M) — Input Sanitization
14. REM-060 (M) — Code Comments and Docstrings
15. REM-063 (M) — Mobile Responsiveness Audit
16. REM-065 (M) — Performance Monitoring Dashboard
17. REM-042 (M) — Context API Migration
18. REM-050 (M) — External API Resilience
19. REM-051 (M) — XSS Vulnerability Audit
20. REM-049 (L) — QA Automation
21. REM-045 (L) — JSON Indexing PostgreSQL
22. REM-053 (M) — PostgreSQL Setup (Migration Phase 1)
23. REM-054 (M) — Schema Translation (Migration Phase 2)
24. REM-055 (L) — Data Migration Script (Migration Phase 3)
25. REM-056 (M) — Application Code Changes (Migration Phase 4)
26. REM-057 (M) — Cutover & Monitoring (Migration Phase 5)
27. REM-067 (M) — Final QA and UAT

## Processo para cada story

1. Leia o arquivo `docs/stories/STORY-REM-XXX.md`
2. Verifique o Status — se já for "Done", pule para a próxima
3. Implemente TODOS os critérios de aceitação exatamente como especificado
4. Escreva testes cobrindo a implementação
5. Execute os testes:
   - Frontend: `cd frontend && npm test -- --run 2>&1 | tail -10`
   - Backend (se a story tocar backend): `cd backend && python -m pytest -x -q 2>&1 | tail -10`
6. Corrija qualquer falha antes de continuar
7. Atualize o arquivo da story: marque todos os AC com [x], Status: "Ready for Review", atualize File List e Change Log
8. Faça commit: `git add -A && git commit -m "feat: <descrição> [REM-XXX]"`
9. Faça push: `git push origin main`
10. Passe para a próxima story

## Regras importantes

- Siga os padrões existentes no codebase (React + Vite + Vitest no frontend, FastAPI + pytest no backend)
- Não invente features além do que está nos critérios de aceitação
- Se uma story tiver dependência de infraestrutura externa (ex: PostgreSQL real), documente o que foi feito e marque como implementado condicionalmente
- Para stories de banco de dados que requerem migração real, crie os scripts/migrations mas não execute-os em produção

## Conclusão

Quando TODAS as 27 stories estiverem implementadas e com push feito, output exatamente:

<promise>ALL STORIES COMPLETE</promise>
