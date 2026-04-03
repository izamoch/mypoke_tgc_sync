# 🏗️ Architecture: MyPoke Sync Service

## 🛠️ Stack Tecnológico
- **Backend:** Python 3.11+ (Asíncrono).
- **Database Principal:** Supabase (PostgreSQL).
- **Database Backup:** SQLite (local).
- **API Clients:** HTTPX (Asíncrono) para TCGDex y PokéAPI.
- **Image Analysis:** ImageHash (pHash) para firmas visuales.

## 🧩 Flujo de Sincronización
1. **Extraction:** Se descarga el catálogo de TCGDex.
2. **Strategy Filter:** Se aplica la rotación de hashes para decidir qué cartas necesitan actualización de precios (Premium, Standard, o Untracked).
3. **Enrichment:** Se solicita información adicional a PokéAPI para cartas de especies no mapeadas.
4. **Upsert:** Se sincroniza contra Supabase usando transacciones atómicas.
5. **Replication:** Se vuelca el estado final de la DB a un archivo SQLite local.

## ⚙️ Procesos Críticos
- **Rate Limiting:** El servicio respeta las cuotas de TCGDex y PokéAPI mediante delays configurables.
- **Error Reporting:** Tras cada ejecución, se genera un reporte en markdown en `reports/` y se envía a un webhook de Discord si está configurado.
