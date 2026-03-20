-- Migration 004: Adiciona colunas faltantes ao schema SQLite
-- Contexto: colunas adicionadas ao modelo SQLAlchemy mas não migradas ao DB existente

-- processes.phase_warning: aviso de classificação incerta (DCP TJRJ, etc.)
ALTER TABLE processes ADD COLUMN phase_warning TEXT;

-- processes.deleted_at: suporte a soft delete (SoftDeleteMixin)
ALTER TABLE processes ADD COLUMN deleted_at DATETIME;

-- movements.deleted_at: suporte a soft delete (SoftDeleteMixin)
ALTER TABLE movements ADD COLUMN deleted_at DATETIME;
