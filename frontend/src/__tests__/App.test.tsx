// @vitest-environment jsdom
import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import App from '../App'

test('renders App component without crashing and shows get started text', () => {
  render(<App />)
  const element = screen.getByText(/Get started/i)
  expect(element).toBeDefined()
})
