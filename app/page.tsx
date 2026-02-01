'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { db } from '@/lib/db'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Database as DatabaseIcon, Search, List, CheckCircle, Clock, TrendingUp, AlertCircle, PlayCircle, Loader2 } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import { toast } from 'sonner'
import { useEffect } from 'react'

type Listing = any
type SyncHistory = any

interface Stats {
  totalSources: number
  totalCriteria: number
  totalListings: number
  availableListings: number
  lastSync: SyncHistory | null
}

export default function DashboardPage() {
  const queryClient = useQueryClient()

  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: () => db.getStats(),
  })

  const { data: recentListings } = useQuery<Listing[]>({
    queryKey: ['recent-listings'],
    queryFn: () => db.getListings({ limit: 5 }),
  })

  const { data: syncHistory } = useQuery<SyncHistory[]>({
    queryKey: ['sync-history'],
    queryFn: () => db.getSyncHistory(5),
  })

  const { data: searchStatus } = useQuery({
    queryKey: ['search-status'],
    queryFn: () => db.getSearchStatus(),
    refetchInterval: (query) => (query.state.data?.isRunning ? 1000 : false),
  })

  const triggerSearchMutation = useMutation({
    mutationFn: () => db.triggerSearch(),
    onSuccess: () => {
      toast.success('Suche gestartet!', {
        description: 'Die Quellen werden jetzt durchsucht...',
      })
      queryClient.invalidateQueries({ queryKey: ['search-status'] })
    },
    onError: (error: Error) => {
      toast.error('Fehler beim Starten', {
        description: error.message,
      })
    },
  })

  useEffect(() => {
    if (searchStatus?.isRunning === false && searchStatus?.startedAt) {
      // Search just finished, refresh data
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      queryClient.invalidateQueries({ queryKey: ['recent-listings'] })
      queryClient.invalidateQueries({ queryKey: ['sync-history'] })
      toast.success('Suche abgeschlossen!', {
        description: `${searchStatus.progress.sourcesChecked} Quellen durchsucht`,
      })
    }
  }, [searchStatus?.isRunning])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="text-muted-foreground">Laden...</div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'Quellen',
      value: stats?.totalSources || 0,
      icon: DatabaseIcon,
      description: 'Aktive Suchquellen',
      color: 'text-blue-600',
    },
    {
      title: 'Suchkriterien',
      value: stats?.totalCriteria || 0,
      icon: Search,
      description: 'Gespeicherte Uhrenmodelle',
      color: 'text-purple-600',
    },
    {
      title: 'Gefundene Listings',
      value: stats?.totalListings || 0,
      icon: List,
      description: 'Insgesamt gefunden',
      color: 'text-green-600',
    },
    {
      title: 'Verfügbar',
      value: stats?.availableListings || 0,
      icon: CheckCircle,
      description: 'Noch verfügbar',
      color: 'text-emerald-600',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Übersicht über dein Watch Service Monitoring
          </p>
        </div>
        <Button
          onClick={() => triggerSearchMutation.mutate()}
          disabled={searchStatus?.isRunning || triggerSearchMutation.isPending}
          className="gap-2"
        >
          {searchStatus?.isRunning ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Suche läuft... ({searchStatus.progress.sourcesChecked}/{searchStatus.progress.totalSources})
            </>
          ) : (
            <>
              <PlayCircle className="h-4 w-4" />
              Suche starten
            </>
          )}
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title} className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <p className="text-3xl font-bold mt-2">{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stat.description}
                  </p>
                </div>
                <Icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </Card>
          )
        })}
      </div>

      {/* Last Sync Info */}
      {stats?.lastSync && (
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold">Letzter Suchlauf</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Datum</p>
                  <p className="font-medium">{formatDate(stats.lastSync.date)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <p className={`font-medium ${
                    stats.lastSync.status === 'Success' ? 'text-green-600' :
                    stats.lastSync.status === 'Partial' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {stats.lastSync.status}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Quellen geprüft</p>
                  <p className="font-medium">{stats.lastSync.sources_checked}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Neue Listings</p>
                  <p className="font-medium">{stats.lastSync.listings_saved}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Recent Listings */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Neueste Listings</h2>
        {recentListings && recentListings.length > 0 ? (
          <div className="space-y-3">
            {recentListings.map((listing) => (
              <Card key={listing.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold">
                      {listing.manufacturer} {listing.model}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {listing.reference_number && `Ref. ${listing.reference_number} • `}
                      {listing.condition} • {listing.location || 'Standort unbekannt'}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>{listing.source}</span>
                      <span>•</span>
                      <span>{formatDate(listing.date_found)}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    {listing.price && (
                      <p className="text-lg font-bold">
                        {new Intl.NumberFormat('de-DE', {
                          style: 'currency',
                          currency: listing.currency,
                        }).format(listing.price)}
                      </p>
                    )}
                    <span className={`inline-block mt-2 px-2 py-1 text-xs rounded-full ${
                      listing.availability === 'Available'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {listing.availability === 'Available' ? 'Verfügbar' : 'Verkauft'}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <List className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">Noch keine Listings gefunden</p>
            <p className="text-sm text-muted-foreground mt-1">
              Der nächste Suchlauf findet zur vollen Stunde statt
            </p>
          </Card>
        )}
      </div>

      {/* Sync History */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Suchhistorie</h2>
        {syncHistory && syncHistory.length > 0 ? (
          <div className="space-y-2">
            {syncHistory.map((sync) => (
              <Card key={sync.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {sync.status === 'Success' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : sync.status === 'Partial' ? (
                      <AlertCircle className="h-5 w-5 text-yellow-600" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <p className="font-medium">{sync.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(sync.date)} • {sync.duration_seconds}s
                      </p>
                    </div>
                  </div>
                  <div className="text-right text-sm">
                    <p className="font-medium">
                      {sync.listings_saved} neue Listings
                    </p>
                    <p className="text-muted-foreground">
                      {sync.sources_checked} Quellen geprüft
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">Noch keine Suchläufe</p>
          </Card>
        )}
      </div>
    </div>
  )
}
