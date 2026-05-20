from http.server import BaseHTTPRequestHandler
import json
import os
from fpdf import FPDF
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # 1. Coletar dados do formulário
        rdo_date = data.get('date', '')
        rdo_area = data.get('area', '')
        rdo_supervisor = data.get('supervisor', '')
        activities = data.get('activities', [])
        crew = data.get('crew', [])
        obs = data.get('observations', 'Sin observaciones.')

        # 2. Gerar o arquivo PDF na pasta temporária do servidor (/tmp)
        pdf_path = "/tmp/reporte_diario.pdf"
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho do PDF
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "REPORTE DIARIO DE ACTIVIDADES", ln=True, align="C")
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Frentes de Trabajo - Copiapó Solar | Área: {rdo_area}", ln=True, align="C")
        pdf.line(10, 30, 200, 30)
        pdf.ln(5)
        
        # Informações Gerais
        pdf.set_font("Arial", "B", 11)
        pdf.cell(40, 8, "Fecha:", 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(50, 8, f"{rdo_date}", 1)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(40, 8, "  Supervisor:", 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(60, 8, f"{rdo_supervisor}", 1, ln=True)
        pdf.ln(5)
        
        # Tabela de Atividades
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "1. Descripción de Actividades", ln=True)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(110, 8, "Descripción", 1)
        pdf.cell(40, 8, "Unidad", 1)
        pdf.cell(40, 8, "Total", 1, ln=True)
        
        pdf.set_font("Arial", "", 10)
        for act in activities:
            pdf.cell(110, 8, f" {act['description']}", 1)
            pdf.cell(40, 8, f" {act['unit']}", 1)
            pdf.cell(40, 8, f" {act['total']}", 1, ln=True)
        pdf.ln(5)
        
        # Equipe presente
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"2. Personal Directo (Presentes: {len(crew)})", ln=True)
        pdf.set_font("Arial", "", 10)
        for worker in crew:
            pdf.cell(0, 6, f" [X] {worker}", ln=True)
        pdf.ln(5)
        
        # Observações
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "3. Observaciones / Comentarios", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 8, f"{obs}", 1)
        
        # Salvar o arquivo PDF gerado
        pdf.output(pdf_path)

        # 3. Conectar com o Google Drive usando as credenciais do cofre da Vercel
        try:
            creds_json = os.environ.get('GOOGLE_CREDENTIALS')
            folder_id = os.environ.get('DRIVE_FOLDER_ID')
            
            creds_info = json.loads(creds_json)
            credentials = service_account.Credentials.from_service_account_info(creds_info)
            
            # Construir o serviço de conexão com o Drive
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Configurar o arquivo para upload
            file_metadata = {
                'name': f"RDO_{rdo_date.replace('-', '')}_{rdo_supervisor.split()[0]}.pdf",
                'parents': [folder_id]
            }
            media = MediaFileUpload(pdf_path, mimetype='application/pdf')
            
            # Executar o Upload real
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            resposta_api = (
                f"✅ ¡ÉXITO TOTAL!\n\n"
                f"El motor de Python procesó los datos y generó o arquivo PDF oficial.\n"
                f"El archivo fue subido exitosamente a la carpeta compartida de Google Drive.\n\n"
                f"📂 Detalles del archivo:\n"
                f"• Nombre: {file_metadata['name']}\n"
                f"• ID en Google Drive: {uploaded_file.get('id')}\n\n"
                f"Ya puedes revisar tu carpeta en Google Drive corporativo, el PDF ya está allá disponible para el equipo."
            )
        except Exception as e:
            resposta_api = f"❌ Error al conectar o subir a Google Drive: {str(e)}"

        # 4. Enviar a resposta de volta para a tela do celular
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "success",
            "message": resposta_api
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
