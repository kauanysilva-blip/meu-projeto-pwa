from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Ler o tamanho dos dados enviados pela página web
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 2. Transformar o texto recebido em um objeto Python (Dicionário)
        data = json.loads(post_data.decode('utf-8'))
        
        # 3. Pegar as informações que o usuário digitou lá na tela
        user_name = data.get('name', 'Usuário Anônimo')
        user_message = data.get('message', '')
        
        # 4. Configurar a resposta do servidor (Status 200 = Tudo OK)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # 5. Criar a mensagem que o Python vai devolver para a tela do celular
        response_data = {
            "status": "success",
            "message": f"🐍 [Python da Vercel] Sucesso! Eu recebi o seu relato. Se a API do Drive estivesse ativa, o arquivo com o texto '{user_message}' seria gerado para o(a) {user_name} agora!"
        }
        
        # 6. Enviar de volta para a página web
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
