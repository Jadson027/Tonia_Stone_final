// chat.js

const ws = new WebSocket('ws://127.0.0.1:8000/ws/chat');

document.getElementById('botaoEnviar').addEventListener('click', () => {
    const messageInput = document.getElementById('inputMensagem');
    const message = messageInput.value.trim();

    if (message === '') return;

    // Adiciona a mensagem do usuário ao chat
    const chatDiv = document.getElementById('chat');
    chatDiv.innerHTML += `
        <section class="msg-opcoes">
            <img class="foto" src="../img/icon-user.svg" alt="usuário">
            <div class="mensagem enviada">
                <p>${message}</p>
            </div>
        </section>
    `;
    messageInput.value = '';

    // Envia a mensagem para o WebSocket
    ws.send(message);
});

ws.onmessage = function(event) {
    const data = event.data;
    const chatDiv = document.getElementById('chat');
    // Adiciona a resposta da IA ao chat
    chatDiv.innerHTML += `
        <section class="msg-opcoes">
            <img class="foto" src="../img/icon-assistant.svg" alt="assistente">
            <div class="mensagem recebida">
                <p>${data}</p>
            </div>
        </section>
    `;
    chatDiv.scrollTop = chatDiv.scrollHeight;  // Scroll automático
};

// Enviar mensagem ao pressionar Enter
document.getElementById('inputMensagem').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('botaoEnviar').click();
    }
});
