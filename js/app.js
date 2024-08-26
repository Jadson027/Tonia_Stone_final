const relatorio = document.querySelector(".page-relatorio");
const chat = document.querySelector(".chat-assistente");
const openExplicacao = document.querySelector(".open-explicacao");

// Funções auxiliares para criar elementos e abrir/fechar seções explicativas
function criaDiv() {
    const div = document.createElement('div');
    return div;
}

function abrirExplicacao(el) {
    const div = el.parentNode;
    const open = div.nextElementSibling;
    return open;
}

// Função para enviar a mensagem do usuário para o backend Flask
function enviarMensagem() {
    const input = document.querySelector('.input-chat input');
    const mensagem = input.value.trim();

    if (mensagem !== '') {
        mostrarMensagemEnviada(mensagem);
        input.value = '';

        // Envia a mensagem para o backend Flask
        fetch('/chat', {  // Alterado para a rota '/chat'
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: mensagem }),  // Alterado para 'message' para combinar com o backend
        })
        .then(response => response.json())
        .then(data => {
            mostrarMensagemRecebida(data.response);  // Alterado para 'response' para combinar com o backend
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    }
}

// Função para mostrar a mensagem enviada pelo usuário no chat
function mostrarMensagemEnviada(mensagem) {
    const secaoChat = document.querySelector('.chat');
    const novaMensagem = document.createElement('section');
    novaMensagem.classList.add('msg-user', 'mensagem', 'enviada');
    novaMensagem.innerHTML = `<p>${mensagem}</p>`;
    secaoChat.appendChild(novaMensagem);
    secaoChat.scrollTop = secaoChat.scrollHeight;
}

// Função para mostrar a mensagem recebida da IA no chat
function mostrarMensagemRecebida(mensagem) {
    const secaoChat = document.querySelector('.chat');
    const novaMensagem = document.createElement('section');
    novaMensagem.classList.add('msg-opcoes', 'mensagem', 'recebida');
    novaMensagem.innerHTML = `
        <img class="foto" src="../img/icon-assistant.svg" alt="assistente">
        <div class="mensagem recebida">
            <p>${mensagem}</p>
        </div>
    `;
    secaoChat.appendChild(novaMensagem);
    secaoChat.scrollTop = secaoChat.scrollHeight;
}

// Listener para detectar cliques e executar ações correspondentes
document.addEventListener('click', e => {
    e.preventDefault();
    const el = e.target;

    if (el.classList.contains('relatorio')) {
        if (relatorio.classList.contains('active')) {
            relatorio.classList.remove('active');
        } else {
            relatorio.classList.add('active');
        }
    }

    if (el.classList.contains('assistente-tonia')) {
        if (chat.classList.contains('active')) {
            chat.classList.remove('active');
            relatorio.classList.add('active');
        } else {
            chat.classList.add('active');
            relatorio.classList.remove('active');
        }
    }

    if (el.classList.contains('open-explicacao')) {
        const open = abrirExplicacao(el);
        if (open.classList.contains('active')) {
            open.classList.remove('active');
        } else {
            open.classList.add('active');
        }
    }

    if (el.closest('.input-chat img')) {
        enviarMensagem();
    }
});

// Listener para enviar a mensagem ao pressionar "Enter"
document.querySelector('.input-chat input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        enviarMensagem();
    }
});
