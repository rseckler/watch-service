'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tantml:parameter>@tanstack/react-query'
import { db } from '@/lib/db'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { X } from 'lucide-react'

type Criteria = any

interface CriteriaDialogProps {
  open: boolean
  onClose: () => void
  editingCriteria: Criteria | null
}

const COUNTRIES = [
  'Germany',
  'Austria',
  'Switzerland',
  'Netherlands',
  'Belgium',
  'France',
  'Italy',
  'Spain',
]

export function CriteriaDialog({
  open,
  onClose,
  editingCriteria,
}: CriteriaDialogProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    manufacturer: '',
    model: '',
    reference_number: '',
    year: '',
    allowed_countries: [] as string[],
    active: true,
    notes: '',
  })

  useEffect(() => {
    if (editingCriteria) {
      setFormData({
        manufacturer: editingCriteria.manufacturer,
        model: editingCriteria.model,
        reference_number: editingCriteria.reference_number || '',
        year: editingCriteria.year?.toString() || '',
        allowed_countries: editingCriteria.allowed_countries || [],
        active: editingCriteria.active,
        notes: editingCriteria.notes || '',
      })
    } else {
      setFormData({
        manufacturer: '',
        model: '',
        reference_number: '',
        year: '',
        allowed_countries: ['Germany'],
        active: true,
        notes: '',
      })
    }
  }, [editingCriteria])

  const createMutation = useMutation({
    mutationFn: (data: Database['public']['Tables']['watch_search_criteria']['Insert']) =>
      db.createCriteria(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['criteria'] })
      onClose()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Database['public']['Tables']['watch_search_criteria']['Update']> }) =>
      db.updateCriteria(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['criteria'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const data = {
      name: `${formData.manufacturer} ${formData.model}`,
      manufacturer: formData.manufacturer,
      model: formData.model,
      reference_number: formData.reference_number || null,
      year: formData.year ? parseInt(formData.year) : null,
      allowed_countries: formData.allowed_countries.length > 0 ? formData.allowed_countries : null,
      active: formData.active,
      notes: formData.notes || null,
    }

    if (editingCriteria) {
      updateMutation.mutate({ id: editingCriteria.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const toggleCountry = (country: string) => {
    setFormData((prev) => ({
      ...prev,
      allowed_countries: prev.allowed_countries.includes(country)
        ? prev.allowed_countries.filter((c) => c !== country)
        : [...prev.allowed_countries, country],
    }))
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">
            {editingCriteria ? 'Suchkriterium bearbeiten' : 'Neues Suchkriterium'}
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Manufacturer */}
          <div>
            <Label htmlFor="manufacturer">Hersteller *</Label>
            <Input
              id="manufacturer"
              value={formData.manufacturer}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, manufacturer: e.target.value }))
              }
              placeholder="z.B. Rolex, Omega, IWC"
              required
            />
          </div>

          {/* Model */}
          <div>
            <Label htmlFor="model">Modell *</Label>
            <Input
              id="model"
              value={formData.model}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, model: e.target.value }))
              }
              placeholder="z.B. Submariner, Speedmaster"
              required
            />
          </div>

          {/* Reference Number */}
          <div>
            <Label htmlFor="reference_number">Referenznummer (optional)</Label>
            <Input
              id="reference_number"
              value={formData.reference_number}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, reference_number: e.target.value }))
              }
              placeholder="z.B. 116610LN"
            />
          </div>

          {/* Year */}
          <div>
            <Label htmlFor="year">Baujahr (optional)</Label>
            <Input
              id="year"
              type="number"
              value={formData.year}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, year: e.target.value }))
              }
              placeholder="z.B. 2020"
              min="1900"
              max={new Date().getFullYear()}
            />
          </div>

          {/* Allowed Countries */}
          <div>
            <Label>Erlaubte Länder</Label>
            <p className="text-sm text-muted-foreground mb-3">
              Wähle die Länder aus, aus denen du Listings sehen möchtest
            </p>
            <div className="grid grid-cols-2 gap-2">
              {COUNTRIES.map((country) => (
                <label
                  key={country}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={formData.allowed_countries.includes(country)}
                    onChange={() => toggleCountry(country)}
                    className="rounded"
                  />
                  <span className="text-sm">{country}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Active */}
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.active}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, active: e.target.checked }))
                }
                className="rounded"
              />
              <span className="text-sm font-medium">Aktiv (wird bei Suche berücksichtigt)</span>
            </label>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notizen (optional)</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, notes: e.target.value }))
              }
              placeholder="Zusätzliche Informationen..."
              rows={3}
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={onClose}>
              Abbrechen
            </Button>
            <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
              {editingCriteria ? 'Speichern' : 'Hinzufügen'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
