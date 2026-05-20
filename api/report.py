from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 1. Converter os dados do formulário estruturado para objeto Python
        data = json.loads(post_data.decode('utf-8'))
        
        # 2. Ler as variáveis organizadas do RDO
        rdo_date = data.get('date', '')
        rdo_area = data.get('area', '')
        rdo_supervisor = data.get('supervisor', '')
        activities = data.get('activities', [])
        crew = data.get('crew', [])
        obs = data.get('observations', 'Sin observaciones.')

        # 3. Processar o texto das atividades dinâmicas recebidas
        activities_text = ""
        for i, act in enumerate(activities, 1):
            activities_text += f"   • Atividade {i}: {act['description']} | Prod: {act['total']} {act['unit']}\n"

        # 4. Configurar o cabeçalho de resposta da API
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # 5. Criar a mensagem de sucesso que comprova o recebimento completo
        msg_sucesso = (
            f"✅ 🐍 [SERVIDOR PYTHON DA VERCEL]:\n"
            f"¡Reporte Diario de Obra (RDO) recibido con éxito para el proyecto Copiapó Solar!\n\n"
            f"📊 RESUMEN PROCESADO:\n"
            f"• Fecha del reporte: {rdo_date}\n"
            f"• Frente / Área: {rdo_area}\n"
            f"• Supervisor/Capataz: {rdo_supervisor}\n\n"
            f"📋 PRODUCCIÓN REGISTRADA:\n{activities_text}\n"
            f"👥 PERSONAL OPERATIVO:\n"
            f"   • {len(crew)} trabajadores registrados como PRESENTES hoy en campo.\n\n"
            f"📝 COMENTARIOS:\n   \"{obs}\"\n\n"
            f"💡 PRÓXIMO NIVEL: Con la API de Drive activa, este resumen generaría el PDF oficial "
            f"con logos de Elecnor/Atlas y lo guardaría directamente en tu carpeta."
        )

        response_data = {
            "status": "success",
            "message": msg_sucesso
        }
        
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
