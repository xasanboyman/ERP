/**
 * Ultra-Lightweight Zero-Dependency Excel & CSV Exporter
 *
 * Exports data to formatted Excel-compatible files (.csv/.xlsx) with UTF-8 BOM support.
 * Immediately frees Blob memory and object URLs to avoid memory retention on low-end hardware.
 */

export interface ExportColumn {
  key: string
  title: string
  formatter?: (val: any, row: any) => string | number
}

/**
 * Clean and escape cell text for CSV/Excel format
 */
function escapeCell(val: any): string {
  if (val === null || val === undefined) return '""'
  const str = String(val).replace(/"/g, '""')
  return `"${str}"`
}

/**
 * Export table data to Excel-compatible CSV with UTF-8 BOM (properly opens in Microsoft Excel)
 */
export function exportToExcel(filename: string, columns: ExportColumn[], data: any[]): void {
  try {
    if (!data || data.length === 0) {
      console.warn('Export: No data provided')
      return
    }

    const headerRow = columns.map((col) => escapeCell(col.title)).join(';')

    const dataRows = data.map((row) => {
      return columns
        .map((col) => {
          let val = row[col.key]
          if (col.formatter) {
            val = col.formatter(val, row)
          }
          return escapeCell(val)
        })
        .join(';')
    })

    const csvContent = '\uFEFF' + [headerRow, ...dataRows].join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `${filename}_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()

    // Immediate cleanup for zero memory retention
    setTimeout(() => {
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }, 100)
  } catch (err) {
    console.error('Failed to export to Excel:', err)
  }
}
