# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

- **Feature:** [`feature-integracao-datajud.md`](feature-integracao-datajud.md) - Definição da busca na API
- **Decision:** [`decision-integracao-datajud`](decision-integracao-datajud) - Arquitetura do serviço de integração (Service Pattern + httpx)
- **Project Initialization:** Context Mesh inicializado
- **Documentation:** Criação do [`project-intent`](project-intent) definindo objetivos de consulta ao DataJud
- **Decision:** [`decision-stack`](decision-stack) - Definido Python (FastAPI) e React

### Fixed

- **Backend:** Ajuste de imports e inicialização do dotenv para evitar `ModuleNotFoundError`/`NameError` ao iniciar a API.
- **DataJud:** Seleção automática da instância mais recente quando houver múltiplos retornos, com metadados no `raw_data`.

---

**Last Updated:** 2026-02-07
