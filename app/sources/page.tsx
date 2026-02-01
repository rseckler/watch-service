'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { db } from '@/lib/db'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ToggleLeft, ToggleRight, ExternalLink, AlertCircle, CheckCircle, Plus, Edit } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import { SourceDialog } from '@/components/source-dialog'

type Source = any

export default function SourcesPage() {
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingSource, setEditingSource] = useState<Source | null>(null)

  const { data: sources, isLoading } = useQuery<Source[]>({
    queryKey: ['sources'],
    queryFn: () => db.getSources(),
  })

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) =>
      db.updateSource(id, { active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const handleToggleActive = (id: string, currentActive: boolean) => {
    toggleActiveMutation.mutate({ id, active: !currentActive })
  }

  const handleEdit = (source: Source) => {
    setEditingSource(source)
    setDialogOpen(true)
  }

  const handleAdd = () => {
    setEditingSource(null)
    setDialogOpen(true)
  }

  const activeCount = sources?.filter((s) => s.active).length || 0
  const errorCount = sources?.filter((s) => s.error_count > 0).length || 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="text-muted-foreground">Laden...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Quellen</h1>
          <p className="text-muted-foreground mt-2">
            Verwalte die Webseiten, die durchsucht werden
          </p>
        </div>
        <Button onClick={handleAdd} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Quelle
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div>
              <p className="text-2xl font-bold">{activeCount}</p>
              <p className="text-sm text-muted-foreground">Aktive Quellen</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-8 w-8 text-yellow-600" />
            <div>
              <p className="text-2xl font-bold">{sources?.length || 0}</p>
              <p className="text-sm text-muted-foreground">Gesamt</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-8 w-8 text-red-600" />
            <div>
              <p className="text-2xl font-bold">{errorCount}</p>
              <p className="text-sm text-muted-foreground">Mit Fehlern</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Sources grouped by type */}
      {['Dealer', 'Forum', 'Marketplace'].map((type) => {
        const sourcesOfType = sources?.filter((s) => s.type === type) || []
        if (sourcesOfType.length === 0) return null

        return (
          <div key={type}>
            <h2 className="text-xl font-semibold mb-3">{type}s</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sourcesOfType.map((source) => (
                <Card key={source.id} className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold">{source.name}</h3>
                        <button
                          onClick={() => handleToggleActive(source.id, source.active)}
                          className="text-muted-foreground hover:text-foreground transition-colors"
                          title={source.active ? 'Deaktivieren' : 'Aktivieren'}
                        >
                          {source.active ? (
                            <ToggleRight className="h-5 w-5 text-green-600" />
                          ) : (
                            <ToggleLeft className="h-5 w-5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleEdit(source)}
                          className="text-muted-foreground hover:text-foreground transition-colors"
                          title="Bearbeiten"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                      </div>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary hover:underline flex items-center gap-1"
                      >
                        {source.domain}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Typ:</span>
                      <span className="font-medium">{source.scraper_type}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Rate Limit:</span>
                      <span className="font-medium">{source.rate_limit_seconds}s</span>
                    </div>
                    {source.requires_auth && (
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Auth:</span>
                        <span className="font-medium text-yellow-600">Erforderlich</span>
                      </div>
                    )}
                    {source.error_count > 0 && (
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Fehler:</span>
                        <span className="font-medium text-red-600">
                          {source.error_count}
                        </span>
                      </div>
                    )}
                  </div>

                  {source.last_successful_scrape && (
                    <div className="mt-3 pt-3 border-t text-xs text-muted-foreground">
                      Letzter Erfolg: {formatDate(source.last_successful_scrape)}
                    </div>
                  )}

                  {source.notes && (
                    <div className="mt-3 pt-3 border-t text-sm text-muted-foreground italic">
                      {source.notes}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )
      })}

      <SourceDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        editingSource={editingSource}
      />
    </div>
  )
}
