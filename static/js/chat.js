// ---- Chat logic ---- //

async function sendMessage() {
  const input = document.getElementById("userInput");
  const msg = input.value.trim();
  if (!msg) return;

  appendMessage(msg, 'user');
  input.value = '';

  try {
    const res = await fetch("/get", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ msg })
    });
    const data = await res.json();
    appendMessage(data.reply, 'bot');
  } catch (error) {
    appendMessage("⚠️ Error: unable to reach the server.", 'bot');
  }
}

function appendMessage(text, sender) {
  const div = document.createElement('div');
  div.classList.add('msg', sender);
  div.textContent = text;
  document.getElementById('messages').appendChild(div);

  const messages = document.getElementById('messages');
  messages.scrollTop = messages.scrollHeight;
}

// Optional: allow pressing "Enter" to send
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("userInput").addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
  });
});
