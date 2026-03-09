-- Migration 005: Add phase_source to processes and search_history
-- Story: Fusion Integration
-- Author: @dev
-- Description: Tracks whether phase was classified via DataJud or Fusion/PAV

-- Add phase_source to processes table
-- Values: 'datajud' | 'fusion_api' | 'fusion_sql' | null (legacy/unknown)
ALTER TABLE processes ADD COLUMN phase_source VARCHAR(20) DEFAULT 'datajud';

-- Add phase_source to search_history table
ALTER TABLE search_history ADD COLUMN phase_source VARCHAR(20);
