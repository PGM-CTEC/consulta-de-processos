# Tarefas

## 1. Refatoração da Organização de Arquivos

- [ ] Mover scripts de diagnóstico e correção da raiz para `backend/scripts/` ou `scripts/`
- [ ] Mover documentações (.md) da raiz para `docs/`
- [ ] Limpar arquivos temporários ou desnecessários na raiz
- [ ] Organizar o frontend se houver redundância (ex: `frontend-alt`)

## 2. Configuração Dinâmica do Frontend (JSON)

- [ ] Criar arquivo `frontend/public/config/labels.json` com os campos de texto
- [ ] Modificar o frontend para carregar este JSON no início da aplicação (ex: via Context ou Hook)
- [ ] Substituir strings hardcoded por referências ao objeto de configuração

## 3. Aba de Histórico

- [ ] **Backend**: Criar modelo e tabela para `History` (se ainda não existir)
- [ ] **Backend**: Criar rotas API `GET /history`, `DELETE /history`
- [ ] **Frontend**: Criar componente de aba "Histórico"
- [ ] **Frontend**: Implementar visualização dos resultados salvos
- [ ] **Frontend**: Adicionar botão "Limpar Histórico"

## 4. Verificação e Finalização

- [ ] Testar persistência do histórico
- [ ] Testar mudança de labels via JSON
- [ ] Garantir que o `launcher.py` continue funcionando com a nova estrutura
- [ ] Atualizar `tasks/lessons.md` com aprendizados

## Revisão

- Pendente
