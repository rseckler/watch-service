# Migration: Supabase → Neon (Vercel Postgres)

## Was wurde geändert?

**Vorher:** Supabase PostgreSQL (shared instance mit Blackfire)
**Nachher:** Neon PostgreSQL (dedizierte Instanz für Watch_Service)

## Änderungen im Code

1. **package.json:** `@supabase/supabase-js` → `@vercel/postgres`
2. **lib/supabase.ts → lib/db.ts:** Umgeschrieben auf raw SQL queries
3. **Alle Pages:** Import von `lib/supabase` → `lib/db`
4. **Types:** Entfernt (verwenden jetzt `any` für Flexibilität)

## Setup-Schritte (bereits erledigt auf Vercel)

### 1. Neon Database erstellt
- Name: `withered-haze-73755759`
- Region: Frankfurt (eu-central-1)
- Automatische Environment Variables in Vercel

### 2. Tables erstellen

Gehe zu **Vercel Postgres SQL Editor:**
https://vercel.com/robin-secklers-projects/watch-service/stores/postgres_withered-haze-73755759

**Schritt 1:** Führe `migrations/001_initial_schema.sql` aus
**Schritt 2:** Führe `scripts/populate-sources.sql` aus

### 3. Fertig!

Nach dem Deployment sollte alles funktionieren:
- Dashboard: https://watch-service.vercel.app/
- Sources: https://watch-service.vercel.app/sources (sollte 17 Quellen zeigen)
- Criteria: https://watch-service.vercel.app/criteria
- Listings: https://watch-service.vercel.app/listings

## Vorteile der Migration

✅ **Dedizierte Instanz:** Keine Konflikte mit Blackfire_service
✅ **Kostenlos:** Neon Free Tier (100 Projekte, 0.5GB pro Projekt)
✅ **Serverless:** Automatisches Scaling
✅ **Vercel Integration:** Nahtlose Integration mit einem Klick
✅ **Kürzlich günstiger:** 25% Preissenkung in 2025

## SQL-Dateien

- `migrations/001_initial_schema.sql` - Erstellt alle 4 Tabellen
- `scripts/populate-sources.sql` - Fügt 17 Quellen hinzu

## Environment Variables (automatisch von Vercel erstellt)

```
POSTGRES_URL
POSTGRES_PRISMA_URL
POSTGRES_URL_NON_POOLING
POSTGRES_USER
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_DATABASE
```

Diese werden automatisch von Vercel injiziert - nichts manuell konfigurieren!
