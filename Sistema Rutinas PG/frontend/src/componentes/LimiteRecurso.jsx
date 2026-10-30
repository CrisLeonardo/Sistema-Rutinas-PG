import { Component } from 'react'

/** Mantiene el texto y el registro cuando falla un recurso opcional. */
export default class LimiteRecurso extends Component {
  state = { fallo: false }
  static getDerivedStateFromError() { return { fallo: true } }
  render() { return this.state.fallo ? this.props.respaldo : this.props.children }
}
