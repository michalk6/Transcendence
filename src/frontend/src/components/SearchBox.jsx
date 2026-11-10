import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'

export default function SearchBox({ value, onChange, onSubmit, placeholder }) {
  return (
    <Form onSubmit={onSubmit} className="d-flex gap-2 mb-2">
      <Form.Control
        size="sm"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <Button size="sm" type="submit" variant="outline-secondary">
        Search
      </Button>
    </Form>
  )
}
