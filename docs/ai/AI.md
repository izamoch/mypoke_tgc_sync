# 🧠 Sync Service AI Context Anchor

Bienvenida, IA. Este servicio es crítico para que la app móvil tenga datos frescos. No rompas la lógica de "Smart Sync" ni modifiques los modelos de Supabase sin actualizar el código de la app móvil (repositorio `scanmon-tracker-app`).

## 📜 Estado Actual
- El servicio está operativo y corriendo tareas programadas.
- La cobertura de tests es del 100% en la lógica de estrategia de sincronización.
- Se ha implementado el enriquecimiento con PokéAPI.

## 🛠️ Tareas Pendientes
- [ ] Implementar un retry-exponential-backoff para las peticiones a PokéAPI (a veces falla por rate limit).
- [ ] Optimizar la query de replicación a SQLite (actualmente tarda ~1min en volcar 10k cartas).
- [ ] Añadir validación de esquemas con Pydantic antes de los Upserts en Supabase.

## 📊 Últimos Cambios
- [2026-04-03]: **Refactor de Limpieza y Estandarización.**
  - Creación de este sistema de anclaje de contexto en `docs/ai/`.
  - Verificación de la estructura del proyecto y estándares de Ruff/Mypy.
  - Sincronización de premisas de negocio en `VISION.md`.
