import { describe, it, expect } from 'vitest'

describe('CCC Basic Test', () => {
  it('should run tests', () => {
    expect(1 + 1).toBe(2)
  })

  it('should have package.json', () => {
    const pkg = require('../../package.json')
    expect(pkg.name).toBeDefined()
  })
})