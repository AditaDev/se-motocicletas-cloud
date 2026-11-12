-- MIGRACIÓN OPCIONAL: SOLO si ya importaste el SQL anterior de 5 tablas.
-- Haz primero un BACKUP completo. Ejecuta UNA SOLA VEZ en la base existente.
-- Conserva los usuarios y las consultas anteriores.
-- No ejecutar en una instalación nueva que ya tenga estas columnas.
ALTER TABLE usuario
    MODIFY correo VARCHAR(254) NOT NULL,
    ADD COLUMN intentos_fallidos INT NOT NULL DEFAULT 0,
    ADD COLUMN bloqueado_hasta DATETIME NULL,
    ADD COLUMN fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE consulta
    ADD COLUMN token_consulta VARCHAR(36) NULL,
    ADD COLUMN resultado_json LONGTEXT NULL,
    ADD UNIQUE KEY uq_consulta_token (token_consulta);

-- El modelo original ya tiene consulta.id_hipotesis y FKs hacia ambas entidades.
-- Los registros anteriores sin resultado_json conservarán sus datos básicos.
