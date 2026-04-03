# 🎯 Project Vision: Pokémon TCG Data Sync

## 💡 Propósito
Motor de sincronización incremental encargado de alimentar MyPoke con datos premium de TCGDex y PokéAPI.

## 🚀 Premisas del Motor (Inamovibles)
- **Smart Sync Strategy**: No saturar APIs externas. Rotación de hashes para precios y metadatos.
- **Lore Enrichment**: Los datos base de TCGDex se enriquecen con cadenas evolutivas y lore de PokéAPI.
- **Atomic Sync**: Una carta no se actualiza a medias. Si falla la actualización de precios, se revierte la transacción para esa carta.
- **Data Replica**: Mantener siempre una réplica local en SQLite (/data/poke_tgc.sqlite) para debugging y backups rápidos.
