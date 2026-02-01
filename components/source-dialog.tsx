'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { db } from '@/lib/db'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { X } from 'lucide-react'

type Source = any

interface SourceDialogProps {
  open: boolean
  onClose: () => void
  editingSource: Source | null
}

const SOURCE_TYPES = ['Dealer', 'Forum', 'Marketplace']
const SCRAPER_TYPES = ['Static', 'Dynamic', 'Forum', 'Marketplace']

export function SourceDialog({
  open,
  onClose,
  editingSource,
}: SourceDialogProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    domain: '',
    type: 'Dealer',
    scraper_type: 'Static',
    active: true,
    requires_auth: false,
    rate_limit_seconds: 2,
    search_url_template: '',
    listing_selector: '',
    title_selector: '',
    price_selector: '',
    link_selector: '',
    image_selector: '',
    auth_username_env: '',
    auth_password_env: '',
    notes: '',
  })

  useEffect(() => {
    if (editingSource) {
      setFormData({
        name: editingSource.name,
        url: editingSource.url,
        domain: editingSource.domain,
        type: editingSource.type,
        scraper_type: editingSource.scraper_type,
        active: editingSource.active,
        requires_auth: editingSource.requires_auth,
        rate_limit_seconds: editingSource.rate_limit_seconds,
        search_url_template: editingSource.search_url_template || '',
        listing_selector: editingSource.listing_selector || '',
        title_selector: editingSource.title_selector || '',
        price_selector: editingSource.price_selector || '',
        link_selector: editingSource.link_selector || '',
        image_selector: editingSource.image_selector || '',
        auth_username_env: editingSource.auth_username_env || '',
        auth_password_env: editingSource.auth_password_env || '',
        notes: editingSource.notes || '',
      })
    } else {
      setFormData({
        name: '',
        url: '',
        domain: '',
        type: 'Dealer',
        scraper_type: 'Static',
        active: true,
        requires_auth: false,
        rate_limit_seconds: 2,
        search_url_template: '',
        listing_selector: '',
        title_selector: '',
        price_selector: '',
        link_selector: '',
        image_selector: '',
        auth_username_env: '',
        auth_password_env: '',
        notes: '',
      })
    }
  }, [editingSource, open])

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await fetch('/api/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Failed to create source')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      onClose()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      db.updateSource(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const data = {
      name: formData.name,
      url: formData.url,
      domain: formData.domain,
      type: formData.type,
      scraper_type: formData.scraper_type,
      active: formData.active,
      requires_auth: formData.requires_auth,
      rate_limit_seconds: formData.rate_limit_seconds,
      search_url_template: formData.search_url_template || null,
      listing_selector: formData.listing_selector || null,
      title_selector: formData.title_selector || null,
      price_selector: formData.price_selector || null,
      link_selector: formData.link_selector || null,
      image_selector: formData.image_selector || null,
      auth_username_env: formData.auth_username_env || null,
      auth_password_env: formData.auth_password_env || null,
      notes: formData.notes || null,
    }

    if (editingSource) {
      updateMutation.mutate({ id: editingSource.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">
              {editingSource ? 'Quelle bearbeiten' : 'Neue Quelle'}
            </h2>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                />
              </div>

              <div>
                <Label htmlFor="domain">Domain *</Label>
                <Input
                  id="domain"
                  value={formData.domain}
                  onChange={(e) =>
                    setFormData({ ...formData, domain: e.target.value })
                  }
                  placeholder="example.com"
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="url">URL *</Label>
              <Input
                id="url"
                type="url"
                value={formData.url}
                onChange={(e) =>
                  setFormData({ ...formData, url: e.target.value })
                }
                placeholder="https://example.com"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="type">Typ *</Label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) =>
                    setFormData({ ...formData, type: e.target.value })
                  }
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  required
                >
                  {SOURCE_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="scraper_type">Scraper Typ *</Label>
                <select
                  id="scraper_type"
                  value={formData.scraper_type}
                  onChange={(e) =>
                    setFormData({ ...formData, scraper_type: e.target.value })
                  }
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  required
                >
                  {SCRAPER_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="active"
                  checked={formData.active}
                  onChange={(e) =>
                    setFormData({ ...formData, active: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="active" className="cursor-pointer">
                  Aktiv
                </Label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="requires_auth"
                  checked={formData.requires_auth}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      requires_auth: e.target.checked,
                    })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="requires_auth" className="cursor-pointer">
                  Benötigt Login
                </Label>
              </div>
            </div>

            <div>
              <Label htmlFor="rate_limit">Rate Limit (Sekunden)</Label>
              <Input
                id="rate_limit"
                type="number"
                value={formData.rate_limit_seconds}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    rate_limit_seconds: parseInt(e.target.value),
                  })
                }
                min="1"
                max="60"
              />
            </div>

            {/* Search Config */}
            <div>
              <Label htmlFor="search_url">
                Search URL Template
                <span className="text-xs text-muted-foreground ml-2">
                  Nutze {'{manufacturer}'} und {'{model}'}
                </span>
              </Label>
              <Input
                id="search_url"
                value={formData.search_url_template}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    search_url_template: e.target.value,
                  })
                }
                placeholder="https://example.com/search?q={manufacturer}+{model}"
              />
            </div>

            {/* CSS Selectors */}
            <div className="space-y-3">
              <h3 className="font-semibold text-sm">CSS Selectors</h3>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="listing_selector" className="text-xs">
                    Listing Container
                  </Label>
                  <Input
                    id="listing_selector"
                    value={formData.listing_selector}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        listing_selector: e.target.value,
                      })
                    }
                    placeholder=".product-item"
                  />
                </div>
                <div>
                  <Label htmlFor="title_selector" className="text-xs">
                    Title
                  </Label>
                  <Input
                    id="title_selector"
                    value={formData.title_selector}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        title_selector: e.target.value,
                      })
                    }
                    placeholder=".title"
                  />
                </div>
                <div>
                  <Label htmlFor="price_selector" className="text-xs">
                    Price
                  </Label>
                  <Input
                    id="price_selector"
                    value={formData.price_selector}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        price_selector: e.target.value,
                      })
                    }
                    placeholder=".price"
                  />
                </div>
                <div>
                  <Label htmlFor="link_selector" className="text-xs">
                    Link
                  </Label>
                  <Input
                    id="link_selector"
                    value={formData.link_selector}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        link_selector: e.target.value,
                      })
                    }
                    placeholder="a.link"
                  />
                </div>
              </div>
            </div>

            {/* Auth Config */}
            {formData.requires_auth && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="auth_user">Username ENV Variable</Label>
                  <Input
                    id="auth_user"
                    value={formData.auth_username_env}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        auth_username_env: e.target.value,
                      })
                    }
                    placeholder="SOURCE_USERNAME"
                  />
                </div>
                <div>
                  <Label htmlFor="auth_pass">Password ENV Variable</Label>
                  <Input
                    id="auth_pass"
                    value={formData.auth_password_env}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        auth_password_env: e.target.value,
                      })
                    }
                    placeholder="SOURCE_PASSWORD"
                  />
                </div>
              </div>
            )}

            <div>
              <Label htmlFor="notes">Notizen</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                rows={3}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="submit" className="flex-1">
                {editingSource ? 'Speichern' : 'Erstellen'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="flex-1"
              >
                Abbrechen
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
