const SENDER_COLORS = ['lightcoral', 'mediumpurple', 'lightblue', 'lightsalmon', 'lightgreen', 'pink']

export function getSenderColor(senderId) {
  return SENDER_COLORS[senderId % SENDER_COLORS.length]
}
