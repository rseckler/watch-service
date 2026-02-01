'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { db } from '@/lib/db'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Edit, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { CriteriaDialog } from '@/components/criteria-dialog'
import { formatDate } from '@/lib/utils'

type Criteria = any

export default function CriteriaPage() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingCriteria, setEditingCriteria] = useState<Criteria | null>(null)
  const queryClient = useQueryClient()

  const { data: criteria, isLoading } = useQuery<Criteria[]>({
    queryKey: ['criteria'],
    queryFn: () => db.getCriteria(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => db.deleteCriteria(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['criteria'] })
    },
  })

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) =>
      db.updateCriteria(id, { active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['criteria'] })
    },
  })

  const handleEdit = (criteria: Criteria) => {
    setEditingCriteria(criteria)
    setDialogOpen(true)
  }

  const handleAdd = () => {
    setEditingCriteria(null)
    setDialogOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Möchtest du dieses Suchkriterium wirklich löschen?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleToggleActive = (id: string, currentActive: boolean) => {
    toggleActiveMutation.mutate({ id, active: !currentActive })
  }

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Suchkriterien</h1>
          <p className="text-muted-foreground mt-2">
            Verwalte die Uhrenmodelle, nach denen du suchen möchtest
          </p>
        </div>
        <Button onClick={handleAdd} size="lg">
          <Plus className="h-4 w-4 mr-2" />
          Neue Uhr hinzufügen
        </Button>
      </div>

      {/* Criteria List */}
      {criteria && criteria.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {criteria.map((item) => (
            <Card key={item.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">{item.name}</h3>
                    <button
                      onClick={() => handleToggleActive(item.id, item.active)}
                      className="text-muted-foreground hover:text-foreground transition-colors"
                      title={item.active ? 'Deaktivieren' : 'Aktivieren'}
                    >
                      {item.active ? (
                        <ToggleRight className="h-5 w-5 text-green-600" />
                      ) : (
                        <ToggleLeft className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <p>
                      <span className="font-medium">Hersteller:</span> {item.manufacturer}
                    </p>
                    <p>
                      <span className="font-medium">Modell:</span> {item.model}
                    </p>
                    {item.reference_number && (
                      <p>
                        <span className="font-medium">Referenz:</span> {item.reference_number}
                      </p>
                    )}
                    {item.year && (
                      <p>
                        <span className="font-medium">Jahr:</span> {item.year}
                      </p>
                    )}
                    {item.allowed_countries && item.allowed_countries.length > 0 && (
                      <p>
                        <span className="font-medium">Länder:</span>{' '}
                        {item.allowed_countries.join(', ')}
                      </p>
                    )}
                  </div>
                  {item.notes && (
                    <p className="text-sm text-muted-foreground mt-3 italic">
                      {item.notes}
                    </p>
                  )}
                </div>
                <div className="flex gap-2 ml-4">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEdit(item)}
                    title="Bearbeiten"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(item.id)}
                    title="Löschen"
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="text-xs text-muted-foreground pt-3 border-t">
                Erstellt: {formatDate(item.created_at)}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <div className="max-w-md mx-auto">
            <Plus className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Noch keine Suchkriterien</h3>
            <p className="text-muted-foreground mb-6">
              Füge Uhrenmodelle hinzu, nach denen du suchen möchtest. Das System
              wird dann alle konfigurierten Quellen stündlich durchsuchen.
            </p>
            <Button onClick={handleAdd} size="lg">
              <Plus className="h-4 w-4 mr-2" />
              Erste Uhr hinzufügen
            </Button>
          </div>
        </Card>
      )}

      {/* Add/Edit Dialog */}
      <CriteriaDialog
        open={dialogOpen}
        onClose={() => {
          setDialogOpen(false)
          setEditingCriteria(null)
        }}
        editingCriteria={editingCriteria}
      />
    </div>
  )
}
