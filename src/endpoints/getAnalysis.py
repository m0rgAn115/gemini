import json 
import logging
from flask import jsonify, request
import google.generativeai as genai


def getAnalysisData(app):
    """ This function is used to get analysis from data """
    
    @app.route('/get-analysis', methods=['POST'])
    def get_analysis():
        try:
            if request.content_type != 'application/json':
                return jsonify({'error': 'Content-Type must be application/json'}), 415

            data = request.get_json()
            
            # Verificar si data está vacío
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            model = genai.GenerativeModel("gemini-1.5-flash-latest",
                system_instruction="Eres un asistente y tu nombre es Tepoz. Tu objetivo es generar un análisis con base a los movimientos de la cuenta que recibes, haciendo recomendaciones u observaciones para mejorar la salud financiera de las personas."
            )

            # Crear el prompt correctamente formateado
            schema = {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "object",
                        "properties": {
                            "totalDeposits": {
                                "type": "number",
                                "description": "Total de depósitos realizados"
                            },
                            "totalExpenses": {
                                "type": "number",
                                "description": "Total de gastos realizados"
                            },
                            "netSavings": {
                                "type": "number",
                                "description": "Ahorros netos (total de depósitos - total de gastos)"
                            },
                            "currentBalance": {
                                "type": "number",
                                "description": "Saldo actual de la cuenta"
                            }
                        },
                        "required": ["totalDeposits", "totalExpenses", "netSavings", "currentBalance"]
                    },
                    "recommendations": {
                        "type": "array",
                        "description": "Recomendaciones para mejorar la salud financiera",
                        "items": {
                            "type": "string"
                        }
                    },
                    "observations": {
                        "type": "array",
                        "description": "Observaciones sobre los patrones de gasto",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["summary", "recommendations", "observations"]
            }

            prompt = f'''
            Tepoz, genera un análisis de los movimientos de la cuenta que se reciben en el siguiente JSON:
            {json.dumps(data)}

            Usa este esquema JSON:
            {json.dumps(schema)}
            '''

            response = model.generate_content(prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            logging.debug(f'Response: {response}')
            return jsonify(json.loads(response.text))
        except Exception as e:
            logging.error(f'Error al generar un análisis: {str(e)}')  # Registrar el error
            return jsonify({'error': f'Error al generar un análisis: {str(e)}'}), 500
