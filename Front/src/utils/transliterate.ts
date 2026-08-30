/**
 * Uzbek Latin <-> Cyrillic High-Performance Transliteration Engine
 */

const LATIN_TO_CYRILLIC_RULES: [RegExp, string][] = [
  // Multi-character uppercase
  [/SH/g, 'Ш'],
  [/Sh/g, 'Ш'],
  [/CH/g, 'Ч'],
  [/Ch/g, 'Ч'],
  [/YO/g, 'Ё'],
  [/Yo/g, 'Ё'],
  [/YU/g, 'Ю'],
  [/Yu/g, 'Ю'],
  [/YA/g, 'Я'],
  [/Ya/g, 'Я'],
  [/YE/g, 'Е'],
  [/Ye/g, 'Е'],
  [/O['`‘ʻ’]/g, 'Ў'],
  [/G['`‘ʻ’]/g, 'Ғ'],

  // Multi-character lowercase
  [/sh/g, 'ш'],
  [/ch/g, 'ч'],
  [/yo/g, 'ё'],
  [/yu/g, 'ю'],
  [/ya/g, 'я'],
  [/ye/g, 'е'],
  [/o['`‘ʻ’]/g, 'ў'],
  [/g['`‘ʻ’]/g, 'ғ'],

  // Single uppercase letters
  [/A/g, 'А'],
  [/B/g, 'Б'],
  [/D/g, 'Д'],
  [/E/g, 'Е'],
  [/F/g, 'Ф'],
  [/G/g, 'Г'],
  [/H/g, 'Ҳ'],
  [/I/g, 'И'],
  [/J/g, 'Ж'],
  [/K/g, 'К'],
  [/L/g, 'Л'],
  [/M/g, 'М'],
  [/N/g, 'Н'],
  [/O/g, 'О'],
  [/P/g, 'П'],
  [/Q/g, 'Қ'],
  [/R/g, 'Р'],
  [/S/g, 'С'],
  [/T/g, 'Т'],
  [/U/g, 'У'],
  [/V/g, 'В'],
  [/X/g, 'Х'],
  [/Y/g, 'Й'],
  [/Z/g, 'З'],

  // Single lowercase letters
  [/a/g, 'а'],
  [/b/g, 'б'],
  [/d/g, 'д'],
  [/e/g, 'е'],
  [/f/g, 'ф'],
  [/g/g, 'г'],
  [/h/g, 'ҳ'],
  [/i/g, 'и'],
  [/j/g, 'ж'],
  [/k/g, 'к'],
  [/l/g, 'л'],
  [/m/g, 'м'],
  [/n/g, 'н'],
  [/o/g, 'о'],
  [/p/g, 'п'],
  [/q/g, 'қ'],
  [/r/g, 'р'],
  [/s/g, 'с'],
  [/t/g, 'т'],
  [/u/g, 'у'],
  [/v/g, 'в'],
  [/x/g, 'х'],
  [/y/g, 'й'],
  [/z/g, 'з']
]

// Technical terms, acronyms, and units to preserve
const PRESERVED_TOKENS: RegExp[] = [
  /https?:\/\/[^\s]+/gi,
  /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi,
  /\b(?:COGS|ERP|POS|HR|CRM|API|ID|UID|SKU|USD|UZS|EUR|HTML|CSS|JS|TS|QR|JSON|WS|REST)\b/g,
  /\$[0-9,.\s]+/g
]

export const toCyrillic = (input: string | null | undefined): string => {
  if (!input || typeof input !== 'string') return (input as any) || ''

  // Preserve technical tokens using control characters
  const placeholders: string[] = []
  let text = input

  PRESERVED_TOKENS.forEach((regex) => {
    text = text.replace(regex, (match) => {
      placeholders.push(match)
      return `\x01${placeholders.length - 1}\x02`
    })
  })

  // Apply transliteration
  for (let i = 0; i < LATIN_TO_CYRILLIC_RULES.length; i++) {
    const [pattern, repl] = LATIN_TO_CYRILLIC_RULES[i]
    text = text.replace(pattern, repl)
  }

  // Restore technical tokens
  placeholders.forEach((token, idx) => {
    text = text.replace(`\x01${idx}\x02`, token)
  })

  return text
}
