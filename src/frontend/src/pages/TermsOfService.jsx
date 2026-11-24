import { useNavigate } from 'react-router-dom'
import Container from 'react-bootstrap/Container'
import Button from 'react-bootstrap/Button'
import Header from '../components/Header'
import Footer from '../components/Footer'

export default function TermsOfService({ onNavigate, user }) {
  const navigate = useNavigate()

  return (
    <>
      <Header onNavigate={onNavigate} user={user} />

      <Container className="py-5 legal-text" style={{ maxWidth: '800px' }}>
        <Button
          variant="outline-secondary"
          size="sm"
          className="mb-4"
          onClick={() => navigate(-1)}
        >
          ← Back
        </Button>

        <h1 className="mb-1">Terms of Service</h1>
        <p className="text-body-secondary mb-4">Last updated November 2026</p>

        <p>
          ULTIMATE.TTT allows registered users to play real-time Ultimate Tic-Tac-Toe
          matches, exchange messages with friends, and maintain a personal profile. These
          Terms describe what you can expect from the service and what is expected of you
          while using it.
        </p>

        <h2 className="fs-5 mt-4">1. Your Account</h2>
        <p>
          An account consisting of a username, email address, and password is required to
          play. You are responsible for keeping your login details confidential and for
          all activity carried out under your account. Registering with a username
          intended to impersonate another person, or granting another person access to
          your account, is not permitted.
        </p>

        <h2 className="fs-5 mt-4">2. Playing Fair</h2>
        <p>While using ULTIMATE.TTT, you agree not to:</p>
        <ul>
          <li>Use bots, scripts, or any automated tool to play matches on your behalf.</li>
          <li>Harass, threaten, or abuse other players in chat or elsewhere in the app.</li>
          <li>Create multiple accounts to circumvent match limits or manipulate results.</li>
          <li>Interfere with, overload, or attempt unauthorized access to the service.</li>
        </ul>

        <h2 className="fs-5 mt-4">3. Chat Messages and Your Avatar</h2>
        <p>
          You retain ownership of any chat messages you send and any avatar image you
          upload. By submitting this content through the app, you grant us permission to
          store it and display it to the users it was intended for, such as the other
          participants in a given conversation, or your friends and opponents viewing
          your profile.
        </p>

        <h2 className="fs-5 mt-4">4. Suspension and Account Removal</h2>
        <p>
          We reserve the right to suspend or close any account that violates the
          obligations described in section 2. You may stop using the service at any
          time, and if you wish to have your account removed entirely, please contact
          the project maintainers.
        </p>

        <h2 className="fs-5 mt-4">5. No Warranty</h2>
        <p>
          ULTIMATE.TTT is a student project developed for the 42 school curriculum, based
          on the ft_transcendence subject. It is provided "as is", with no promise that it
          will always be available or free of bugs, and it is not intended for production
          or commercial use.
        </p>
      </Container>

      <Footer />
    </>
  )
}
