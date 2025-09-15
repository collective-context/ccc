import { describe, it, expect } from 'vitest'
import { existsSync } from 'fs'

describe('CCC Helpers', () => {
  it('should have expected project structure', () => {
    expect(existsSync('./lib')).toBe(true)
    expect(existsSync('./ccc')).toBe(true)
    expect(existsSync('./README.md')).toBe(true)
  })

  it('should have vitest config', () => {
    expect(existsSync('./vitest.config.ts')).toBe(true)
  })
})