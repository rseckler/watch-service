import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number | null, currency: string = 'EUR'): string {
  if (price === null) return 'N/A'

  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: currency,
  }).format(price)
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString('de-DE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
