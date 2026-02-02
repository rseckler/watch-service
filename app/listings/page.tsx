'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { db } from '@/lib/db'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ExternalLink, Filter, X, ArrowUpDown } from 'lucide-react'
import { formatDate, formatPrice } from '@/lib/utils'

type Listing = any
type Source = any

type SortField = 'price' | 'date_found' | 'source' | 'manufacturer' | 'model'
type SortDirection = 'asc' | 'desc'

export default function ListingsPage() {
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [availabilityFilter, setAvailabilityFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('date_found')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const { data: listings, isLoading } = useQuery<Listing[]>({
    queryKey: ['listings', availabilityFilter, sourceFilter],
    queryFn: () =>
      db.getListings({
        availability: availabilityFilter || undefined,
        source: sourceFilter || undefined,
      }),
  })

  const { data: sources } = useQuery<Source[]>({
    queryKey: ['sources'],
    queryFn: () => db.getSources(),
  })

  const filteredListings = listings
    ?.filter((listing) => {
      if (!searchQuery) return true
      const search = searchQuery.toLowerCase()
      return (
        listing.manufacturer?.toLowerCase().includes(search) ||
        listing.model?.toLowerCase().includes(search) ||
        listing.reference_number?.toLowerCase().includes(search)
      )
    })
    .sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'price':
          aValue = a.price || 0
          bValue = b.price || 0
          break
        case 'date_found':
          aValue = new Date(a.date_found || 0).getTime()
          bValue = new Date(b.date_found || 0).getTime()
          break
        case 'source':
          aValue = a.source || ''
          bValue = b.source || ''
          break
        case 'manufacturer':
          aValue = a.manufacturer || ''
          bValue = b.manufacturer || ''
          break
        case 'model':
          aValue = a.model || ''
          bValue = b.model || ''
          break
        default:
          return 0
      }

      // Compare values
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      } else {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
      }
    })

  const clearFilters = () => {
    setSourceFilter('')
    setAvailabilityFilter('')
    setSearchQuery('')
    setSortField('date_found')
    setSortDirection('desc')
  }

  const hasFilters = sourceFilter || availabilityFilter || searchQuery

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
      <div>
        <h1 className="text-3xl font-bold">Listings</h1>
        <p className="text-muted-foreground mt-2">
          Alle gefundenen Uhren-Listings
        </p>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">Filter & Sortierung</span>
          {hasFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="ml-auto"
            >
              <X className="h-4 w-4 mr-1" />
              Zurücksetzen
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <Input
              placeholder="Suche nach Hersteller, Modell..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Source Filter */}
          <div>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
            >
              <option value="">Alle Quellen</option>
              {sources?.map((source) => (
                <option key={source.id} value={source.name}>
                  {source.name}
                </option>
              ))}
            </select>
          </div>

          {/* Availability Filter */}
          <div>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={availabilityFilter}
              onChange={(e) => setAvailabilityFilter(e.target.value)}
            >
              <option value="">Alle Status</option>
              <option value="Available">Verfügbar</option>
              <option value="Sold">Verkauft</option>
              <option value="Unknown">Unbekannt</option>
            </select>
          </div>

          {/* Sort Dropdown */}
          <div>
            <div className="flex gap-2">
              <select
                className="flex h-10 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={`${sortField}-${sortDirection}`}
                onChange={(e) => {
                  const [field, direction] = e.target.value.split('-') as [
                    SortField,
                    SortDirection
                  ]
                  setSortField(field)
                  setSortDirection(direction)
                }}
              >
                <optgroup label="Nach Preis">
                  <option value="price-asc">Preis aufsteigend</option>
                  <option value="price-desc">Preis absteigend</option>
                </optgroup>
                <optgroup label="Nach Datum">
                  <option value="date_found-desc">Neueste zuerst</option>
                  <option value="date_found-asc">Älteste zuerst</option>
                </optgroup>
                <optgroup label="Nach Name">
                  <option value="manufacturer-asc">Hersteller A-Z</option>
                  <option value="manufacturer-desc">Hersteller Z-A</option>
                  <option value="model-asc">Modell A-Z</option>
                  <option value="model-desc">Modell Z-A</option>
                </optgroup>
                <optgroup label="Nach Quelle">
                  <option value="source-asc">Quelle A-Z</option>
                  <option value="source-desc">Quelle Z-A</option>
                </optgroup>
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Listings */}
      {filteredListings && filteredListings.length > 0 ? (
        <div>
          <div className="text-sm text-muted-foreground mb-4">
            {filteredListings.length} Listing{filteredListings.length !== 1 && 's'}
          </div>
          <div className="space-y-3">
            {filteredListings.map((listing) => (
              <Card key={listing.id} className="p-5">
                <div className="flex items-start justify-between gap-4">
                  {/* Watch Image */}
                  {listing.image_url && (
                    <img
                      src={listing.image_url}
                      alt={`${listing.manufacturer} ${listing.model}`}
                      className="h-24 w-24 object-cover rounded border flex-shrink-0"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  )}
                  {/* Main Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-1">
                          {listing.manufacturer} {listing.model}
                        </h3>
                        <div className="flex flex-wrap gap-x-3 gap-y-1 text-sm text-muted-foreground">
                          {listing.reference_number && (
                            <span>Ref. {listing.reference_number}</span>
                          )}
                          {listing.year && <span>• {listing.year}</span>}
                          {listing.condition && <span>• {listing.condition}</span>}
                        </div>
                        <div className="flex flex-wrap gap-x-3 gap-y-1 text-sm text-muted-foreground mt-2">
                          <span>{listing.source}</span>
                          {listing.location && (
                            <>
                              <span>•</span>
                              <span>{listing.location}</span>
                            </>
                          )}
                          {listing.seller_name && (
                            <>
                              <span>•</span>
                              <span>{listing.seller_name}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Price & Status */}
                  <div className="text-right flex-shrink-0">
                    {listing.price && (
                      <div className="text-xl font-bold mb-2">
                        {formatPrice(listing.price, listing.currency)}
                      </div>
                    )}
                    <div className="flex items-center gap-2 justify-end">
                      <span
                        className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                          listing.availability === 'Available'
                            ? 'bg-green-100 text-green-800'
                            : listing.availability === 'Sold'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {listing.availability === 'Available'
                          ? 'Verfügbar'
                          : listing.availability === 'Sold'
                          ? 'Verkauft'
                          : 'Unbekannt'}
                      </span>
                      <a
                        href={listing.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-primary hover:underline text-sm"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                    <div className="text-xs text-muted-foreground mt-2">
                      {formatDate(listing.date_found)}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ) : (
        <Card className="p-12 text-center">
          <div className="max-w-md mx-auto">
            <ExternalLink className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Keine Listings gefunden</h3>
            <p className="text-muted-foreground">
              {hasFilters
                ? 'Versuche andere Filter-Einstellungen'
                : 'Sobald neue Uhren gefunden werden, erscheinen sie hier'}
            </p>
          </div>
        </Card>
      )}
    </div>
  )
}
