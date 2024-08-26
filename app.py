from flask import Flask, request, jsonify
from Cerebro import interfaceinicial  # Importe sua função que realiza a lógica da IA

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    usermessage = data.get("message")

#Chama a função que processa a mensagem do usuário e gera a resposta da IA
    response = interfaceinicial(usermessage)

    return jsonify({"response": response})

if __name__ == '__main':
    app.run(debug=True)