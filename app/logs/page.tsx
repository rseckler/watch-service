'use client'

import { useQuery } from '@tanstack/react-query'
import { db } from '@/lib/db'
import { Card } from '@/components/ui/card'
import { CheckCircle, AlertCircle, XCircle, Clock, Database, List as ListIcon, RefreshCw } from 'lucide-react'
import { formatDate } from '@/lib/utils'

type SyncHistory = any

export default function LogsPage() {
  const { data: logs, isLoading, refetch } = useQuery<SyncHistory[]>({
    queryKey: ['sync-history'],
    queryFn: async () => {
      const res = await fetch('/api/sync-history?limit=50')
      if (!res.ok) throw new Error('Failed to fetch logs')
      return res.json()
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="text-muted-foreground">Laden...</div>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Success':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'Partial':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />
      case 'Failed':
        return <XCircle className="h-5 w-5 text-red-600" />
      default:
        return <Clock className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Success':
        return 'bg-green-50 border-green-200'
      case 'Partial':
        return 'bg-yellow-50 border-yellow-200'
      case 'Failed':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">System-Logs</h1>
          <p className="text-muted-foreground mt-2">
            Detaillierte Übersicht aller Suchläufe und Hintergrund-Aktivitäten
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Aktualisieren
        </button>
      </div>

      {/* Stats Summary */}
      {logs && logs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <Database className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{logs.length}</p>
                <p className="text-sm text-muted-foreground">Suchläufe</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-2xl font-bold">
                  {logs.filter((l) => l.status === 'Success').length}
                </p>
                <p className="text-sm text-muted-foreground">Erfolgreich</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <ListIcon className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">
                  {logs.reduce((sum, l) => sum + (l.listings_saved || 0), 0)}
                </p>
                <p className="text-sm text-muted-foreground">Gefundene Listings</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <Clock className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-2xl font-bold">
                  {Math.round(
                    logs.reduce((sum, l) => sum + (l.duration_seconds || 0), 0) / logs.length
                  )}s
                </p>
                <p className="text-sm text-muted-foreground">Ø Dauer</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Logs Timeline */}
      {logs && logs.length > 0 ? (
        <div className="space-y-3">
          {logs.map((log) => (
            <Card
              key={log.id}
              className={`p-5 border-l-4 ${getStatusColor(log.status)}`}
            >
              <div className="flex items-start gap-4">
                {getStatusIcon(log.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-lg">{log.name}</h3>
                    <span className="text-sm text-muted-foreground">
                      {formatDate(log.date)}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-muted-foreground">Status</p>
                      <p className="font-medium">{log.status}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Quellen geprüft</p>
                      <p className="font-medium">
                        {log.sources_checked}
                        {log.sources_failed > 0 && (
                          <span className="text-red-600 ml-1">
                            (-{log.sources_failed})
                          </span>
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Listings gefunden</p>
                      <p className="font-medium">{log.listings_found || 0}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Neue gespeichert</p>
                      <p className="font-medium text-green-600">
                        {log.listings_saved || 0}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                    <span>Duplikate: {log.duplicates_skipped || 0}</span>
                    <span>•</span>
                    <span>Dauer: {log.duration_seconds}s</span>
                  </div>

                  {log.error_message && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                      <p className="font-medium">Fehler:</p>
                      <p className="mt-1">{log.error_message}</p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <Clock className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Noch keine Logs vorhanden</h3>
          <p className="text-muted-foreground">
            Starte einen Suchlauf auf dem Dashboard, um Logs zu sehen
          </p>
        </Card>
      )}
    </div>
  )
}
